from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Iterable

from index_service.models import FileRecord, IndexedRoot, SearchHit, TextChunk


class SQLiteIndexStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def connect(self) -> sqlite3.Connection:
        # 每次操作都新建连接，配合显式关闭，避免 Windows 下数据库文件被锁住。
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with closing(self.connect()) as connection, connection:
            # FTS5 只负责全文检索，原始结构化数据仍然放普通表里，方便后续扩展。
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS indexed_roots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    root_path TEXT NOT NULL UNIQUE,
                    last_indexed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT NOT NULL UNIQUE,
                    size_bytes INTEGER NOT NULL,
                    mtime_ns INTEGER NOT NULL,
                    content_hash TEXT NOT NULL,
                    indexed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS document_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
                );

                CREATE VIRTUAL TABLE IF NOT EXISTS document_chunks_fts
                USING fts5(
                    content,
                    content='document_chunks',
                    content_rowid='id',
                    tokenize='unicode61'
                );

                CREATE TRIGGER IF NOT EXISTS document_chunks_ai
                AFTER INSERT ON document_chunks
                BEGIN
                    INSERT INTO document_chunks_fts(rowid, content)
                    VALUES (new.id, new.content);
                END;

                CREATE TRIGGER IF NOT EXISTS document_chunks_ad
                AFTER DELETE ON document_chunks
                BEGIN
                    INSERT INTO document_chunks_fts(document_chunks_fts, rowid, content)
                    VALUES ('delete', old.id, old.content);
                END;

                CREATE TRIGGER IF NOT EXISTS document_chunks_au
                AFTER UPDATE ON document_chunks
                BEGIN
                    INSERT INTO document_chunks_fts(document_chunks_fts, rowid, content)
                    VALUES ('delete', old.id, old.content);
                    INSERT INTO document_chunks_fts(rowid, content)
                    VALUES (new.id, new.content);
                END;
                """
            )

    def record_roots(self, roots: Iterable[Path]) -> None:
        with closing(self.connect()) as connection, connection:
            connection.executemany(
                """
                INSERT INTO indexed_roots(root_path, last_indexed_at)
                VALUES (?, CURRENT_TIMESTAMP)
                ON CONFLICT(root_path)
                DO UPDATE SET last_indexed_at = excluded.last_indexed_at
                """,
                [(str(root),) for root in roots],
            )

    def list_roots(self) -> list[IndexedRoot]:
        with closing(self.connect()) as connection:
            rows = connection.execute(
                """
                SELECT root_path, last_indexed_at
                FROM indexed_roots
                ORDER BY root_path
                """
            ).fetchall()
        return [
            IndexedRoot(
                root_path=row["root_path"],
                last_indexed_at=row["last_indexed_at"],
            )
            for row in rows
        ]

    def get_file_record(self, path: str) -> FileRecord | None:
        with closing(self.connect()) as connection:
            row = connection.execute(
                """
                SELECT path, size_bytes, mtime_ns, content_hash
                FROM files
                WHERE path = ?
                """,
                (path,),
            ).fetchone()
        if row is None:
            return None
        return FileRecord(
            path=row["path"],
            size_bytes=int(row["size_bytes"]),
            mtime_ns=int(row["mtime_ns"]),
            content_hash=row["content_hash"],
        )

    def upsert_file(self, record: FileRecord) -> int:
        with closing(self.connect()) as connection, connection:
            # 先按路径做 upsert，v1 阶段只保证同一路径文件的最新索引状态。
            cursor = connection.execute(
                """
                INSERT INTO files(path, size_bytes, mtime_ns, content_hash, indexed_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(path)
                DO UPDATE SET
                    size_bytes = excluded.size_bytes,
                    mtime_ns = excluded.mtime_ns,
                    content_hash = excluded.content_hash,
                    indexed_at = CURRENT_TIMESTAMP
                RETURNING id
                """,
                (record.path, record.size_bytes, record.mtime_ns, record.content_hash),
            )
            row = cursor.fetchone()
        return int(row["id"])

    def replace_chunks(self, file_id: int, chunks: Iterable[TextChunk]) -> None:
        chunk_rows = [
            (file_id, chunk.chunk_index, chunk.start_line, chunk.end_line, chunk.content)
            for chunk in chunks
        ]
        with closing(self.connect()) as connection, connection:
            # 当前策略是整文件替换文本块，先求简单稳定，后面再优化成增量更新。
            connection.execute("DELETE FROM document_chunks WHERE file_id = ?", (file_id,))
            if chunk_rows:
                connection.executemany(
                    """
                    INSERT INTO document_chunks(file_id, chunk_index, start_line, end_line, content)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    chunk_rows,
                )

    def delete_missing_files(self, scanned_paths: Iterable[str], indexed_roots: Iterable[Path]) -> int:
        path_set = set(scanned_paths)
        deleted = 0
        with closing(self.connect()) as connection, connection:
            # 只删除本次索引根目录下已经消失的文件，避免误删其他根的数据。
            rows = connection.execute("SELECT id, path FROM files").fetchall()
            for row in rows:
                file_path = row["path"]
                file_id = int(row["id"])
                is_under_root = any(file_path.startswith(str(root)) for root in indexed_roots)
                if is_under_root and file_path not in path_set:
                    connection.execute("DELETE FROM files WHERE id = ?", (file_id,))
                    deleted += 1
        return deleted

    def search(self, query: str, limit: int) -> list[SearchHit]:
        with closing(self.connect()) as connection:
            # 这里直接用 SQLite FTS5 做 v1 搜索，先把“能找到”这件事跑通。
            rows = connection.execute(
                """
                SELECT
                    files.path AS path,
                    document_chunks.chunk_index AS chunk_index,
                    document_chunks.start_line AS start_line,
                    document_chunks.end_line AS end_line,
                    snippet(document_chunks_fts, 0, '[', ']', '...', 18) AS snippet,
                    bm25(document_chunks_fts) AS score
                FROM document_chunks_fts
                JOIN document_chunks ON document_chunks.id = document_chunks_fts.rowid
                JOIN files ON files.id = document_chunks.file_id
                WHERE document_chunks_fts MATCH ?
                ORDER BY score, files.path, document_chunks.chunk_index
                LIMIT ?
                """,
                (query, limit),
            ).fetchall()

        return [
            SearchHit(
                path=row["path"],
                match_type="content",
                chunk_index=int(row["chunk_index"]),
                start_line=int(row["start_line"]),
                end_line=int(row["end_line"]),
                snippet=row["snippet"],
                score=float(row["score"]),
            )
            for row in rows
        ]

    def search_files_by_name(self, query: str, limit: int) -> list[SearchHit]:
        normalized = f"%{query.lower()}%"
        with closing(self.connect()) as connection:
            # 先用简单的路径模糊匹配实现文件检索，后面再考虑更细的排序规则。
            rows = connection.execute(
                """
                SELECT
                    path,
                    CASE
                        WHEN lower(path) LIKE ? THEN 0
                        ELSE 1
                    END AS rank_bucket
                FROM files
                WHERE lower(path) LIKE ?
                ORDER BY rank_bucket, length(path), path
                LIMIT ?
                """,
                (normalized, normalized, limit),
            ).fetchall()

        return [
            SearchHit(
                path=row["path"],
                match_type="filename",
                chunk_index=0,
                start_line=0,
                end_line=0,
                snippet=row["path"],
                score=float(row["rank_bucket"]),
            )
            for row in rows
        ]
