from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


class LocalPathActionService:
    def open_path(self, raw_path: str, mode: str) -> Path:
        target = Path(raw_path).expanduser().resolve()
        if not target.exists():
            raise ValueError(f"Path does not exist: {target}")

        if mode == "file":
            launch_target = target
        elif mode == "parent":
            launch_target = target.parent if target.is_file() else target
        else:
            raise ValueError(f"Unsupported open mode: {mode}")

        _launch_path(launch_target)
        return launch_target


def _launch_path(target: Path) -> None:
    # 先优先兼容当前 Windows 开发环境，保留其他平台的最小兜底。
    if hasattr(os, "startfile"):
        os.startfile(str(target))  # type: ignore[attr-defined]
        return

    if sys.platform == "darwin":
        subprocess.run(["open", str(target)], check=True)
        return

    subprocess.run(["xdg-open", str(target)], check=True)
