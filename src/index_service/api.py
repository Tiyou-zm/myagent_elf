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
    skipped_files: int
    deleted_files: int
    warnings: list[str]


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=50)


class SearchHitResponse(BaseModel):
    path: str
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
            skipped_files=summary.skipped_files,
            deleted_files=summary.deleted_files,
            warnings=summary.warnings,
        )

    @router.post("/search", response_model=SearchResponse)
    def search(request: SearchRequest) -> SearchResponse:
        try:
            summary = search_service.search(request.query, request.limit)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        return SearchResponse(query=summary.query, results=summary.results)

    app = FastAPI(title=settings.app_name)

    @app.get("/healthz", response_model=HealthResponse)
    def healthz() -> HealthResponse:
        # 给后面 Electron 或脚本探活用的最小健康检查。
        return HealthResponse(status="ok")

    app.include_router(router)
    return app
