from __future__ import annotations

from dataclasses import dataclass

from index_service.models import SearchHit
from index_service.storage import SQLiteIndexStore


@dataclass(slots=True)
class SearchSummary:
    # 搜索服务的内部返回结构，避免 API 直接依赖存储层对象。
    query: str
    results: list[SearchHit]


class SearchService:
    def __init__(self, store: SQLiteIndexStore) -> None:
        self.store = store

    def search(self, query: str, limit: int) -> SearchSummary:
        # 先做最小输入校验，把明显无效请求挡在服务层。
        cleaned = query.strip()
        if not cleaned:
            raise ValueError("Query must not be empty.")
        hits = self.store.search(cleaned, limit)
        return SearchSummary(query=cleaned, results=hits)

    def search_files(self, query: str, limit: int) -> SearchSummary:
        cleaned = query.strip()
        if not cleaned:
            raise ValueError("Query must not be empty.")
        hits = self.store.search_files_by_name(cleaned, limit)
        return SearchSummary(
            query=cleaned,
            results=hits,
        )
