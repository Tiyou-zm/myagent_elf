from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FileRecord:
    # 文件表里需要的最小元数据，先不引入更复杂的解析状态。
    path: str
    size_bytes: int
    mtime_ns: int
    content_hash: str


@dataclass(slots=True)
class IndexedRoot:
    # 已登记的索引根目录，便于 API 回显当前服务管理了哪些目录。
    root_path: str
    last_indexed_at: str


@dataclass(slots=True)
class TextChunk:
    # 文本切块后的结构，便于后续补摘要、重排或语义索引。
    chunk_index: int
    start_line: int
    end_line: int
    content: str


@dataclass(slots=True)
class SearchHit:
    # 搜索层统一返回的命中结构，API 层只做序列化。
    path: str
    match_type: str
    chunk_index: int
    start_line: int
    end_line: int
    snippet: str
    score: float
