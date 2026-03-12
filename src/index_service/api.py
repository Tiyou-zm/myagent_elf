from __future__ import annotations

from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel, Field

from index_service.config import get_settings
from index_service.indexing import IndexingService
from index_service.search import SearchService
from index_service.storage import SQLiteIndexStore


class HealthResponse(BaseModel):
    status: str


class IndexRequest(BaseModel):
    # 用户显式提供允许索引的目录，符合项目“只处理授权目录”的边界。
    roots: list[str] = Field(min_length=1)


class IndexResponse(BaseModel):
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
    query: str
    results: list[SearchHitResponse]


def create_app() -> FastAPI:
    settings = get_settings()
    store = SQLiteIndexStore(settings.database_path)
    # 应用启动时先确保基础表结构存在，避免空库时某些接口先访问就报错。
    store.initialize()
    indexing_service = IndexingService(settings, store)
    search_service = SearchService(store)

    router = APIRouter(prefix=settings.api_prefix)

    @router.post("/index", response_model=IndexResponse)
    def build_index(request: IndexRequest) -> IndexResponse:
        # API 层只负责参数校验和错误映射，具体索引逻辑留在服务层。
        try:
            summary = indexing_service.build_index(request.roots)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        return IndexResponse(
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
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        return SearchResponse(
            query=summary.query,
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
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        return SearchResponse(
            query=summary.query,
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

    app = FastAPI(title=settings.app_name)

    @app.get("/healthz", response_model=HealthResponse)
    def healthz() -> HealthResponse:
        # 给后面 Electron 或脚本探活用的最小健康检查。
        return HealthResponse(status="ok")

    app.include_router(router)
    return app
