from __future__ import annotations

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from index_service.actions import LocalPathActionService
from index_service.chat import ChatMessage, ChatReply, ChatService, SuggestedAction
from index_service.config import Settings, get_settings
from index_service.indexing import IndexingService
from index_service.search import SearchService
from index_service.storage import SQLiteIndexStore


class HealthResponse(BaseModel):
    status: str
    message: str


class IndexRequest(BaseModel):
    # 用户显式提供允许索引的目录，符合项目“只处理授权目录”的边界。
    roots: list[str] = Field(min_length=1)


class IndexResponse(BaseModel):
    message: str
    roots: list[str]
    scanned_files: int
    indexed_files: int
    unchanged_files: int
    skipped_files: int
    deleted_files: int
    warnings: list[str]


class IndexedRootResponse(BaseModel):
    root_path: str
    last_indexed_at: str


class RootsResponse(BaseModel):
    message: str
    roots: list[IndexedRootResponse]


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=50)


class SearchHitResponse(BaseModel):
    path: str
    match_type: str
    chunk_index: int
    start_line: int
    end_line: int
    snippet: str
    score: float


class SearchResponse(BaseModel):
    message: str
    query: str
    total_results: int
    results: list[SearchHitResponse]


class ChatMessageRequest(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[ChatMessageRequest] = Field(default_factory=list)
    limit: int = Field(default=5, ge=1, le=10)


class SuggestedActionResponse(BaseModel):
    label: str
    path: str
    mode: str


class ChatResponse(BaseModel):
    message: str
    reply: str
    citations: list[SearchHitResponse]
    actions: list[SuggestedActionResponse]
    used_llm: bool


class OpenPathRequest(BaseModel):
    path: str = Field(min_length=1)
    mode: str = Field(pattern="^(file|parent)$")


class ActionResponse(BaseModel):
    message: str
    path: str
    mode: str


def _bad_request(detail: str) -> HTTPException:
    # 统一无效输入的返回结构，方便前端后续直接展示或分支处理。
    return HTTPException(
        status_code=400,
        detail={
            "code": "bad_request",
            "message": detail,
        },
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    store = SQLiteIndexStore(settings.database_path)
    # 应用启动时先确保基础表结构存在，避免空库时某些接口先访问就报错。
    store.initialize()
    indexing_service = IndexingService(settings, store)
    search_service = SearchService(store)
    chat_service = ChatService(search_service, settings)
    action_service = LocalPathActionService()

    router = APIRouter(prefix=settings.api_prefix)

    @router.post("/index", response_model=IndexResponse)
    def build_index(request: IndexRequest) -> IndexResponse:
        # API 层只负责参数校验和错误映射，具体索引逻辑留在服务层。
        try:
            summary = indexing_service.build_index(request.roots)
        except ValueError as exc:
            raise _bad_request(str(exc)) from exc

        return IndexResponse(
            message=f"Indexing finished. {summary.indexed_files} files updated, {summary.unchanged_files} unchanged.",
            roots=summary.roots,
            scanned_files=summary.scanned_files,
            indexed_files=summary.indexed_files,
            unchanged_files=summary.unchanged_files,
            skipped_files=summary.skipped_files,
            deleted_files=summary.deleted_files,
            warnings=summary.warnings,
        )

    @router.get("/roots", response_model=RootsResponse)
    def list_roots() -> RootsResponse:
        roots = store.list_roots()
        return RootsResponse(
            message=f"{len(roots)} indexed roots registered.",
            roots=[
                IndexedRootResponse(
                    root_path=root.root_path,
                    last_indexed_at=root.last_indexed_at,
                )
                for root in roots
            ]
        )

    @router.post("/search", response_model=SearchResponse)
    def search(request: SearchRequest) -> SearchResponse:
        try:
            summary = search_service.search(request.query, request.limit)
        except ValueError as exc:
            raise _bad_request(str(exc)) from exc

        return SearchResponse(
            message=f"Found {len(summary.results)} content matches.",
            query=summary.query,
            total_results=len(summary.results),
            results=[
                SearchHitResponse(
                    path=hit.path,
                    match_type=hit.match_type,
                    chunk_index=hit.chunk_index,
                    start_line=hit.start_line,
                    end_line=hit.end_line,
                    snippet=hit.snippet,
                    score=hit.score,
                )
                for hit in summary.results
            ],
        )

    @router.post("/search/files", response_model=SearchResponse)
    def search_files(request: SearchRequest) -> SearchResponse:
        try:
            summary = search_service.search_files(request.query, request.limit)
        except ValueError as exc:
            raise _bad_request(str(exc)) from exc

        return SearchResponse(
            message=f"Found {len(summary.results)} filename matches.",
            query=summary.query,
            total_results=len(summary.results),
            results=[
                SearchHitResponse(
                    path=hit.path,
                    match_type=hit.match_type,
                    chunk_index=hit.chunk_index,
                    start_line=hit.start_line,
                    end_line=hit.end_line,
                    snippet=hit.snippet,
                    score=hit.score,
                )
                for hit in summary.results
            ],
        )

    @router.post("/chat", response_model=ChatResponse)
    def chat(request: ChatRequest) -> ChatResponse:
        try:
            reply = chat_service.reply(
                request.message,
                history=[ChatMessage(role=item.role, content=item.content) for item in request.history],
                limit=request.limit,
            )
        except ValueError as exc:
            raise _bad_request(str(exc)) from exc

        return ChatResponse(
            message=reply.message,
            reply=reply.reply,
            citations=[
                SearchHitResponse(
                    path=hit.path,
                    match_type=hit.match_type,
                    chunk_index=hit.chunk_index,
                    start_line=hit.start_line,
                    end_line=hit.end_line,
                    snippet=hit.snippet,
                    score=hit.score,
                )
                for hit in reply.citations
            ],
            actions=[
                SuggestedActionResponse(
                    label=action.label,
                    path=action.path,
                    mode=action.mode,
                )
                for action in reply.actions
            ],
            used_llm=reply.used_llm,
        )

    @router.post("/open", response_model=ActionResponse)
    def open_path(request: OpenPathRequest) -> ActionResponse:
        try:
            opened_path = action_service.open_path(request.path, request.mode)
        except ValueError as exc:
            raise _bad_request(str(exc)) from exc

        if request.mode == "file":
            message = "File open command sent."
        else:
            message = "Directory open command sent."

        return ActionResponse(
            message=message,
            path=str(opened_path),
            mode=request.mode,
        )

    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_allowed_origins),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/healthz", response_model=HealthResponse)
    def healthz() -> HealthResponse:
        # 给后面 Electron 或脚本探活用的最小健康检查。
        return HealthResponse(status="ok", message="Index service is healthy.")

    app.include_router(router)
    return app
