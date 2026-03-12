from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from index_service.config import Settings
from index_service.indexing import IndexingService
from index_service.search import SearchService
from index_service.storage import SQLiteIndexStore


class IndexingServiceTest(unittest.TestCase):
    def test_build_index_and_search(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sample_file = root / "notes.md"
            sample_file.write_text(
                "# Agent Study\n\nPython index service skeleton with SQLite FTS.\n",
                encoding="utf-8",
            )

            settings = Settings(database_path=root / "index.db")
            store = SQLiteIndexStore(settings.database_path)
            indexing_service = IndexingService(settings, store)
            search_service = SearchService(store)

            # 先验证最核心闭环：能建索引，再能搜到刚写入的内容。
            summary = indexing_service.build_index([str(root)])
            self.assertEqual(summary.indexed_files, 1)
            self.assertEqual(summary.unchanged_files, 0)

            results = search_service.search("Python", limit=5)
            self.assertEqual(len(results.results), 1)
            self.assertEqual(results.results[0].match_type, "content")
            self.assertIn("notes.md", str(results.results[0].path))

    def test_incremental_index_and_file_search(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sample_file = root / "agent_notes.md"
            sample_file.write_text(
                "Agent search can find file names and content.\n",
                encoding="utf-8",
            )

            settings = Settings(database_path=root / "index.db")
            store = SQLiteIndexStore(settings.database_path)
            indexing_service = IndexingService(settings, store)
            search_service = SearchService(store)

            first_summary = indexing_service.build_index([str(root)])
            second_summary = indexing_service.build_index([str(root)])

            self.assertEqual(first_summary.indexed_files, 1)
            self.assertEqual(second_summary.indexed_files, 0)
            self.assertEqual(second_summary.unchanged_files, 1)

            file_results = search_service.search_files("agent_notes", limit=5)
            self.assertEqual(len(file_results.results), 1)
            self.assertEqual(file_results.results[0].match_type, "filename")
            self.assertIn("agent_notes.md", file_results.results[0].snippet)

            roots = store.list_roots()
            self.assertEqual(len(roots), 1)
            self.assertEqual(roots[0].root_path, str(root))


if __name__ == "__main__":
    unittest.main()
