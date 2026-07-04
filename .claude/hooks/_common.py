#!/usr/bin/env python3
"""SOFI AI — shared hook helpers.

Tiny, dependency-free utilities reused by the lifecycle hooks
(session_start / stop / post_tool_use). Everything here is best-effort:
callers must wrap usage in try/except and fail OPEN (never break the session).
"""
from __future__ import annotations

import os
import re
from pathlib import Path


def project_root() -> Path:
    """Workspace root — CLAUDE_PROJECT_DIR if set, else this file's grandparent."""
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and Path(env).is_dir():
        return Path(env)
    return Path(__file__).resolve().parents[2]


def projects_dir(root: Path) -> Path:
    """Physical workspace root holding every project (single-root doctrine —
    no symlink). SOFI_PROJECTS_DIR override, else ~/Desktop/projects, else the
    legacy <root>/projects. Mirrors sofi_tools.paths.projects_dir()."""
    env = os.environ.get("SOFI_PROJECTS_DIR")
    if env and Path(env).expanduser().is_dir():
        return Path(env).expanduser().resolve()
    physical = Path.home() / "Desktop" / "projects"
    if physical.is_dir():
        return physical.resolve()
    return root / "projects"


def find_active_project(root: Path) -> Path | None:
    """The project whose _context/STATE.md was touched most recently.

    The doctrine keeps one live brain per project under
    <projects>/<PRJ>/_context/STATE.md; the freshest one is the active focus.
    """
    states = list(projects_dir(root).glob("*/_context/STATE.md"))
    if not states:
        return None
    states.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return states[0].parent.parent  # projects/<PRJ>


def read_state(state_md: Path) -> dict:
    """Parse the leading `key: value` lines of a STATE.md into a dict.

    STATE.md is loose markdown with a front block of `key: value` pairs
    (title, branch, head_sha, gate, active, local_domain, status, ...).
    We grab only simple top-level scalars; anything fancy is ignored.
    """
    out: dict[str, str] = {}
    try:
        for line in state_md.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^([a-z_][a-z0-9_]*):\s+(.+?)\s*$", line)
            if m and m.group(1) not in out:
                out[m.group(1)] = m.group(2)
    except Exception:
        pass
    return out


def next_ticket(handoffs_md: Path) -> str | None:
    """First non-empty, non-heading line of HANDOFFS.md — the next ticket hint."""
    try:
        for line in handoffs_md.read_text(encoding="utf-8", errors="replace").splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                return s[:240]
    except Exception:
        pass
    return None
