from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(slots=True)
class Settings:
    # 先把 v1 的核心运行参数集中在这里，后面再决定是否切到环境变量或配置文件。
    app_name: str = "Agent Study Index Service"
    api_prefix: str = "/api/v1"
    database_path: Path = PROJECT_ROOT / "data" / "index.db"
    cors_allowed_origins: tuple[str, ...] = (
        "http://127.0.0.1:4173",
        "http://localhost:4173",
        "null",
    )
    chunk_size_chars: int = 1200
    chunk_overlap_chars: int = 200
    max_file_size_bytes: int = 2 * 1024 * 1024
    llm_base_url: str | None = field(default_factory=lambda: os.getenv("FEILING_LLM_BASE_URL"))
    llm_api_key: str | None = field(default_factory=lambda: os.getenv("FEILING_LLM_API_KEY"))
    llm_model: str | None = field(default_factory=lambda: os.getenv("FEILING_LLM_MODEL"))
    llm_timeout_seconds: float = field(default_factory=lambda: float(os.getenv("FEILING_LLM_TIMEOUT_SECONDS", "20")))
    allowed_extensions: set[str] = field(
        default_factory=lambda: {
            ".md",
            ".txt",
            ".py",
            ".json",
            ".yaml",
            ".yml",
            ".toml",
            ".ini",
            ".cfg",
            ".csv",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".html",
            ".css",
        }
    )
    skipped_directories: set[str] = field(
        default_factory=lambda: {
            ".git",
            "__pycache__",
            ".venv",
            "node_modules",
            ".idea",
            ".vscode",
        }
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    # 用单例配置避免每次请求重复构造。
    return Settings()
