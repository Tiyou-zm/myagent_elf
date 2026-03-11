from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from index_service.config import Settings
from index_service.models import FileRecord, TextChunk
from index_service.storage import SQLiteIndexStore


@dataclass(slots=True)
class IndexingSummary:
    # 把一次建索引的结果收敛成摘要，后面 API 和前端都能直接复用。
    roots: list[str]
    scanned_files: int
    indexed_files: int
    skipped_files: int
    deleted_files: int
    warnings: list[str]


class IndexingService:
    def __init__(self, settings: Settings, store: SQLiteIndexStore) -> None:
        self.settings = settings
        self.store = store

    def build_index(self, roots: list[str]) -> IndexingSummary:
        # v1 先走“全量扫描指定根目录”的简单路径，先把链路立起来。
        normalized_roots = self._normalize_roots(roots)
        self.store.initialize()
        self.store.record_roots(normalized_roots)

        scanned_files = 0
        indexed_files = 0
        skipped_files = 0
        warnings: list[str] = []
        scanned_paths: list[str] = []

        for root in normalized_roots:
            for file_path in self._iter_candidate_files(root):
                scanned_files += 1
                scanned_paths.append(str(file_path))

                text = self._read_text(file_path)
                if text is None:
                    # 暂时只吃 UTF-8 纯文本，复杂编码和富文档解析后面再补。
                    skipped_files += 1
                    continue

                file_id = self.store.upsert_file(
                    FileRecord(
                        path=str(file_path),
                        size_bytes=file_path.stat().st_size,
                        mtime_ns=file_path.stat().st_mtime_ns,
                        content_hash=hashlib.sha1(text.encode("utf-8")).hexdigest(),
                    )
                )
                self.store.replace_chunks(file_id, build_chunks(text, self.settings))
                indexed_files += 1

        deleted_files = self.store.delete_missing_files(scanned_paths, normalized_roots)

        if not scanned_files:
            warnings.append("No indexable files were found under the requested roots.")

        return IndexingSummary(
            roots=[str(root) for root in normalized_roots],
            scanned_files=scanned_files,
            indexed_files=indexed_files,
            skipped_files=skipped_files,
            deleted_files=deleted_files,
            warnings=warnings,
        )

    def _normalize_roots(self, roots: list[str]) -> list[Path]:
        normalized: list[Path] = []
        for root in roots:
            candidate = Path(root).expanduser().resolve()
            if not candidate.exists():
                raise ValueError(f"Root does not exist: {candidate}")
            if not candidate.is_dir():
                raise ValueError(f"Root is not a directory: {candidate}")
            normalized.append(candidate)

        unique_roots = list(dict.fromkeys(normalized))
        if not unique_roots:
            raise ValueError("At least one root directory is required.")
        return unique_roots

    def _iter_candidate_files(self, root: Path):
        # 先用扩展名和大小做粗过滤，降低 v1 的复杂度和索引成本。
        for path in root.rglob("*"):
            if any(part in self.settings.skipped_directories for part in path.parts):
                continue
            if not path.is_file():
                continue
            if path.suffix.lower() not in self.settings.allowed_extensions:
                continue
            if path.stat().st_size > self.settings.max_file_size_bytes:
                continue
            yield path

    def _read_text(self, path: Path) -> str | None:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return None


def build_chunks(text: str, settings: Settings) -> list[TextChunk]:
    # 先按字符窗口切块，同时保留行号范围，方便结果展示和后续定位。
    chunks: list[TextChunk] = []
    lines = text.splitlines() or [text]
    chunk_lines: list[str] = []
    current_chars = 0
    chunk_start_line = 1
    chunk_index = 0

    for line_number, line in enumerate(lines, start=1):
        rendered_line = line if line.endswith("\n") else f"{line}\n"
        chunk_lines.append(rendered_line)
        current_chars += len(rendered_line)
        if current_chars >= settings.chunk_size_chars:
            chunk_text = "".join(chunk_lines).strip()
            if chunk_text:
                chunks.append(
                    TextChunk(
                        chunk_index=chunk_index,
                        start_line=chunk_start_line,
                        end_line=line_number,
                        content=chunk_text,
                    )
                )
                chunk_index += 1
            chunk_lines = _overlap_tail(chunk_lines, settings.chunk_overlap_chars)
            # 保留一小段重叠文本，减少关键词刚好卡在分块边界时的召回损失。
            chunk_start_line = max(1, line_number - len(chunk_lines) + 1)
            current_chars = sum(len(item) for item in chunk_lines)

    if chunk_lines:
        chunk_text = "".join(chunk_lines).strip()
        if chunk_text:
            chunks.append(
                TextChunk(
                    chunk_index=chunk_index,
                    start_line=chunk_start_line,
                    end_line=len(lines),
                    content=chunk_text,
                )
            )
    return chunks


def _overlap_tail(lines: list[str], overlap_chars: int) -> list[str]:
    if overlap_chars <= 0:
        return []

    # 从块尾回收一段文本作为下一个块的上下文。
    kept: list[str] = []
    total = 0
    for line in reversed(lines):
        kept.append(line)
        total += len(line)
        if total >= overlap_chars:
            break
    kept.reverse()
    return kept
