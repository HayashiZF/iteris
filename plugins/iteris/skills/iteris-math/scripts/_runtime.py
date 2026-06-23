from __future__ import annotations

import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def src_root() -> Path:
    return repo_root() / "src"


def ensure_repo_imports() -> Path:
    src = src_root()
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    return src
