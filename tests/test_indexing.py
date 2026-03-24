from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi.testclient import TestClient

from index_service.api import create_app
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

    def test_api_returns_frontend_friendly_messages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sample_file = root / "notes.md"
            sample_file.write_text(
                "Python service smoke test content.\n",
                encoding="utf-8",
            )

            app = create_app(Settings(database_path=root / "index.db"))
            client = TestClient(app)

            health_response = client.get("/healthz")
            self.assertEqual(health_response.status_code, 200)
            self.assertEqual(health_response.json()["message"], "Index service is healthy.")

            index_response = client.post(
                "/api/v1/index",
                json={"roots": [str(root)]},
            )
            self.assertEqual(index_response.status_code, 200)
            index_payload = index_response.json()
            self.assertIn("message", index_payload)
            self.assertEqual(index_payload["indexed_files"], 1)

            search_response = client.post(
                "/api/v1/search",
                json={"query": "Python", "limit": 5},
            )
            self.assertEqual(search_response.status_code, 200)
            search_payload = search_response.json()
            self.assertIn("message", search_payload)
            self.assertEqual(search_payload["total_results"], 1)
            self.assertEqual(search_payload["results"][0]["match_type"], "content")

            roots_response = client.get("/api/v1/roots")
            self.assertEqual(roots_response.status_code, 200)
            roots_payload = roots_response.json()
            self.assertIn("message", roots_payload)
            self.assertEqual(len(roots_payload["roots"]), 1)

    def test_api_returns_structured_bad_request(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            app = create_app(Settings(database_path=root / "index.db"))
            client = TestClient(app)

            response = client.post(
                "/api/v1/search",
                json={"query": "   ", "limit": 5},
            )
            self.assertEqual(response.status_code, 400)
            payload = response.json()
            self.assertEqual(payload["detail"]["code"], "bad_request")
            self.assertIn("must not be empty", payload["detail"]["message"])

    def test_api_allows_local_frontend_shell_origin(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            app = create_app(Settings(database_path=root / "index.db"))
            client = TestClient(app)

            response = client.options(
                "/api/v1/search",
                headers={
                    "Origin": "http://127.0.0.1:4173",
                    "Access-Control-Request-Method": "POST",
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.headers["access-control-allow-origin"],
                "http://127.0.0.1:4173",
            )

    def test_api_allows_electron_file_origin(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            app = create_app(Settings(database_path=root / "index.db"))
            client = TestClient(app)

            response = client.options(
                "/api/v1/search",
                headers={
                    "Origin": "null",
                    "Access-Control-Request-Method": "POST",
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.headers["access-control-allow-origin"],
                "null",
            )

    def test_api_can_open_file_and_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sample_file = root / "notes.md"
            sample_file.write_text("open action test\n", encoding="utf-8")

            app = create_app(Settings(database_path=root / "index.db"))
            client = TestClient(app)

            with patch("index_service.actions._launch_path") as launch_mock:
                file_response = client.post(
                    "/api/v1/open",
                    json={"path": str(sample_file), "mode": "file"},
                )
                self.assertEqual(file_response.status_code, 200)
                self.assertEqual(file_response.json()["mode"], "file")
                self.assertEqual(file_response.json()["path"], str(sample_file.resolve()))
                launch_mock.assert_called_with(sample_file.resolve())

                parent_response = client.post(
                    "/api/v1/open",
                    json={"path": str(sample_file), "mode": "parent"},
                )
                self.assertEqual(parent_response.status_code, 200)
                self.assertEqual(parent_response.json()["mode"], "parent")
                self.assertEqual(parent_response.json()["path"], str(root.resolve()))
                launch_mock.assert_called_with(root.resolve())

    def test_chat_endpoint_returns_reply_and_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sample_file = root / "notes.md"
            sample_file.write_text(
                "Feiling can answer in bubble style and open files.\n",
                encoding="utf-8",
            )

            app = create_app(Settings(database_path=root / "index.db"))
            client = TestClient(app)
            client.post("/api/v1/index", json={"roots": [str(root)]})

            response = client.post(
                "/api/v1/chat",
                json={
                    "message": "bubble style",
                    "history": [{"role": "user", "content": "之前我在找素材"}],
                    "limit": 5,
                },
            )
            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertEqual(payload["message"], "bubble style")
            self.assertTrue(payload["reply"])
            self.assertGreaterEqual(len(payload["citations"]), 1)
            self.assertGreaterEqual(len(payload["actions"]), 1)
            self.assertEqual(payload["actions"][0]["mode"], "file")
            self.assertFalse(payload["used_llm"])



if __name__ == "__main__":
    unittest.main()
