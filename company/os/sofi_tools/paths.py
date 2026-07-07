"""
paths — resolve the SOFI AI workspace + per-project directories.

Single source of truth for where things live. Every other module asks here
instead of hardcoding paths, so a workspace move only touches this file.
"""
from __future__ import annotations

import os
from pathlib import Path

# Sentinels that mark the workspace root: CLAUDE.md plus the company/ layer
# (v6). engine/ is accepted too so the resolver keeps working on a v5 checkout
# or mid-migration tree (v5 debt #3 paid — the sentinel no longer pins engine/).
_ANCHOR = "CLAUDE.md"
_LAYER_DIRS = ("company", "engine")


def repo_root(start: str | os.PathLike | None = None) -> Path:
    """Walk upward from `start` (or this file) until the workspace root is found."""
    here = Path(start or __file__).resolve()
    for d in (here, *here.parents):
        if (d / _ANCHOR).exists() and any((d / l).is_dir() for l in _LAYER_DIRS):
            return d
    raise FileNotFoundError(
        "SOFI AI workspace root not found (need CLAUDE.md + company/ or engine/). "
        f"Searched from {here}."
    )


def sofi_dir() -> Path:
    """The company layer root — law, nexus, rooms, brain, os."""
    return repo_root() / "company"


def tooling_dir() -> Path:
    """The executable OS layer — sofi_tools, bin/sofi, per-role toolkits."""
    return sofi_dir() / "os"


def nexus_dir() -> Path:
    """The connecting layer — registry.yaml · routing.yaml · gates.yaml · bus/."""
    return sofi_dir() / "nexus"


def projects_dir() -> Path:
    """Physical workspace root holding every project.

    Single-root doctrine (2026-07-01): resolves to the REAL directory, never a
    symlink, so scanning/tooling/CI and the serving layer (Caddy/tunnels) all
    read the same bytes. Override with ``SOFI_PROJECTS_DIR``; defaults to
    ``~/Desktop/projects``. Legacy ``<repo>/projects`` is the last-resort
    fallback for a portable checkout.
    """
    env = os.environ.get("SOFI_PROJECTS_DIR")
    if env:
        return Path(env).expanduser().resolve()
    physical = Path.home() / "Desktop" / "projects"
    if physical.is_dir():
        return physical.resolve()
    return (repo_root() / "projects").resolve()  # legacy fallback


def project_repo(prj: str) -> Path:
    """The project's OWN git repository root (brain lives here, per single-root
    doctrine). Walks up from the project dir to the enclosing ``.git`` toplevel;
    falls back to the project dir itself if it is not (yet) a repo."""
    d = project_dir(prj).resolve()
    for c in (d, *d.parents):
        if (c / ".git").exists():
            return c
    return d


def project_dir(prj: str) -> Path:
    p = projects_dir() / prj
    return p


def context_dir(prj: str) -> Path:
    return project_dir(prj) / "_context"


def brain_file(prj: str, name: str) -> Path:
    """name in {STATE, CONTEXT, DECISIONS, HANDOFFS, LESSONS}.
    LESSONS.md (v5) holds distilled procedural memory written by the reflection engine."""
    return context_dir(prj) / f"{name}.md"


def docs_dir(prj: str) -> Path:
    return project_dir(prj) / "docs"


def src_dir(prj: str) -> Path:
    return project_dir(prj) / "src"


def scratch_dir(prj: str) -> Path:
    """Ephemeral temp-script area for a project. Created on demand; auto-purged."""
    return project_dir(prj) / "_scratch"


def project_exists(prj: str) -> bool:
    return project_dir(prj).is_dir() and context_dir(prj).is_dir()


def list_projects() -> list[str]:
    pd = projects_dir()
    if not pd.is_dir():
        return []
    return sorted(p.name for p in pd.iterdir() if p.is_dir() and (p / "_context").is_dir())
