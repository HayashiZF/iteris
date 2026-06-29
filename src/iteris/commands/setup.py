"""Setup command."""

from __future__ import annotations

import shutil

from iteris import log


def setup() -> None:
    """Check lightweight Iteris prerequisites."""
    rows = []
    # codex/claude CLIs are only required for interactive /goal sessions on that
    # backend; headless agent runs now use the Python SDKs.
    for binary in ["python3", "git", "rg", "tmux", "codex", "claude"]:
        path = shutil.which(binary)
        status = "ok" if path else ("warning" if binary in {"codex", "claude"} else "error")
        detail = path or ("optional interactive executor CLI; headless runs use SDKs" if binary in {"codex", "claude"} else "not found")
        rows.append((binary, status, detail))
    log.results_table(rows, title="Setup checks")
    log.success("Setup check complete")

