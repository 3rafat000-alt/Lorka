#!/usr/bin/env python3
"""
ceo_toolkit — SOFI CEO Agent's automated command console (one file, three engines).

The CEO drives 15 rooms · 104 colleagues across a 9-gate lifecycle. This toolkit is the
"big brain, small mouth" console: orient, delegate, inspect, and gate — each with
one function call, each emitting terse, paste-ready output that spends the fewest
tokens that still clears the bar (Doctrine: *few token do trick*).

Three engines, one module:

  1. Orchestrator        — Routing & Orchestration. One call = one fully-oriented
                           RCCF delegation block (Role · Context · Conditions · Tools),
                           with a local PromptCache so shared context is sent once
                           and referenced by digest thereafter (token saver).

  2. ProjectInspector    — Automated Project Inspection. Walks the project tree
                           (auto-skipping node_modules / vendor / .git / build junk),
                           reads the sensitive/interesting files, and emits a fast
                           Health Check report (stack, gaps, smells, secret leaks).

  3. ComplianceEngine    — Guardrails & Conditions. Declarative conditions checked
                           against an agent's output BEFORE the CEO accepts it, so a
                           gate bar can't be silently skipped.

Design notes
------------
* Zero hard third-party deps. Reuses `sofi_tools` (routing / paths / brain) when the
  package is importable; degrades to self-contained fallbacks when run standalone.
* Pure stdlib. Fail-open on optional niceties, fail-loud on real errors.
* Every public method carries a docstring showing intended CEO usage.

CLI
---
    python ceo_toolkit.py delegate <role> --prj PRJ-XXXX [--task "..."] [--priority CRITICAL]
    python ceo_toolkit.py inspect  <path|PRJ-XXXX>        [--json]
    python ceo_toolkit.py health   <path|PRJ-XXXX>        [--json]
    python ceo_toolkit.py comply   <output-file> --rules rules.json
    python ceo_toolkit.py routes                          # dump the resolved route table

Import
------
    from ceo_toolkit import Orchestrator, ProjectInspector, ComplianceEngine
    ceo = Orchestrator()
    block = ceo.delegate(role="bck-api-engineer", prj="PRJ-SAKK",
                         task="Add refund endpoint", priority="HIGH")
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Iterable, Optional


# ─────────────────────────────────────────────────────────────────────────────
# 0. Bootstrap — locate the sofi_tools package (reuse), fall back to standalone.
# ─────────────────────────────────────────────────────────────────────────────

def _bootstrap_sofi_tools() -> Optional[Any]:
    """Find the `sofi_tools` package by walking up from this file and import it.

    Returns the imported module namespace object, or ``None`` when the toolkit is
    run outside the SOFI workspace. Callers must tolerate ``None`` and use the
    local fallbacks below — the toolkit stays useful standalone.
    """
    here = Path(__file__).resolve()
    for up in here.parents:
        if (up / "sofi_tools").is_dir():
            if str(up) not in sys.path:
                sys.path.insert(0, str(up))
            try:
                import sofi_tools  # type: ignore
                return sofi_tools
            except Exception:
                return None
    return None


_SOFI = _bootstrap_sofi_tools()


def _repo_root() -> Path:
    """Workspace root — via sofi_tools.paths when available, else sentinel walk."""
    if _SOFI is not None:
        try:
            from sofi_tools import paths  # type: ignore
            return paths.repo_root()
        except Exception:
            pass
    here = Path(__file__).resolve()
    for d in (here, *here.parents):
        if (d / "CLAUDE.md").exists() and ((d / "company").is_dir() or (d / "engine").is_dir()):
            return d
    return here.parents[3] if len(here.parents) > 3 else here.parent


def _project_dir(target: str) -> Path:
    """Resolve a CLI target that is EITHER a PRJ-ID OR a filesystem path.

    A bare ``PRJ-XXXX`` resolves under the physical projects root (single-root
    doctrine, no symlink); anything else is treated as a literal path.
    """
    if re.fullmatch(r"PRJ-[A-Za-z0-9]+", target):
        try:
            from sofi_tools import paths  # type: ignore
            return paths.project_dir(target)
        except Exception:
            pass
        return _repo_root() / "projects" / target
    return Path(target).expanduser().resolve()


# ─────────────────────────────────────────────────────────────────────────────
# 1. Shared value types.
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Route:
    """A resolved model·effort·caveman route for a role (cheapest clearing dial)."""
    role: str
    model: str = "workhorse"
    model_id: str = "claude-sonnet-5"
    tier: str = "🔵"
    effort: str = "medium"
    caveman: str = "full"
    gate: str = ""
    budget: str = ""
    priority: str = "—"

    def one_line(self) -> str:
        return (f"{self.model} · {self.effort} · {self.caveman}  "
                f"({self.tier} {self.model_id} | gate {self.gate} | "
                f"budget {self.budget} | prio {self.priority})")


@dataclass
class Delegation:
    """The full result of an orchestration call: the RCCF block + machine fields."""
    role: str
    prj: str
    task: str
    route: Route
    conditions: list[str]
    tools: list[str]
    context_ref: str          # short digest token for cached context (@ctx:xxxx)
    block: str                # the paste-ready RCCF spawn block
    cached: bool              # True when context was reused from cache (token save)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["route"] = asdict(self.route)
        return d


# Canonical agent id → spec path (Operating Prompt lives inside each spec file).
# v6: loaded from the org index (company/nexus/registry.yaml) via sofi_tools.registry —
# no hardcoded roster (v5 debt #4 paid). Empty when running standalone; the
# delegator then prints a `sofi registry <id>` pointer instead of a path.
def _build_spec_path() -> dict[str, str]:
    if _SOFI is not None:
        try:
            from sofi_tools import registry as _reg  # type: ignore
            return {aid: _reg.spec_path(aid) for aid in _reg.agents()}
        except Exception:
            pass
    return {}


SPEC_PATH: dict[str, str] = _build_spec_path()


# ─────────────────────────────────────────────────────────────────────────────
# 2. PromptCache — send shared context ONCE, reference by digest after.
# ─────────────────────────────────────────────────────────────────────────────

class PromptCache:
    """Local, on-disk cache of reusable prompt templates + context blobs.

    Why: re-embedding a project's full context in every delegation burns tokens.
    Instead we store each distinct context blob once under a content hash and hand
    the CEO a short reference token (``@ctx:<8hex>``). A downstream reader (or the
    CEO itself) can ``materialize()`` the token back to full text when — and only
    when — the receiving agent actually lacks it. This operationalizes
    *few token do trick* at the delegation layer.

    Storage: JSON files under ``<repo>/.claude/cache/ceo-prompts/`` (created lazily).
    Safe to delete anytime; it is a cache, never a source of truth.
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        self.dir = cache_dir or (_repo_root() / ".claude" / "cache" / "ceo-prompts")
        self._mem: dict[str, str] = {}   # in-process hot cache

    # -- internal ------------------------------------------------------------
    def _ensure(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _digest(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]

    def _path(self, key: str) -> Path:
        return self.dir / f"{key}.json"

    # -- public API ----------------------------------------------------------
    def store(self, text: str, label: str = "") -> str:
        """Cache a context blob; return its ``@ctx:<hash>`` reference token.

        Idempotent: identical text always maps to the same token, so repeated
        delegations for the same context are free after the first.
        """
        key = self._digest(text)
        self._mem[key] = text
        p = self._path(key)
        if not p.exists():
            self._ensure()
            p.write_text(json.dumps(
                {"label": label, "stored_at": int(time.time()), "text": text},
                ensure_ascii=False, indent=2), encoding="utf-8")
        return f"@ctx:{key}"

    def has(self, ref_or_text: str) -> bool:
        """True if the given ref token OR raw text is already cached."""
        key = self._key_of(ref_or_text)
        return key in self._mem or self._path(key).exists()

    def materialize(self, ref: str) -> Optional[str]:
        """Expand a ``@ctx:<hash>`` token back to its full text, or None if absent."""
        key = self._key_of(ref)
        if key in self._mem:
            return self._mem[key]
        p = self._path(key)
        if p.exists():
            try:
                text = json.loads(p.read_text(encoding="utf-8")).get("text", "")
                self._mem[key] = text
                return text
            except Exception:
                return None
        return None

    def digest_line(self, text: str, max_chars: int = 160) -> str:
        """A one-line human hint of a blob (first non-empty line, clipped).

        Sent ALONGSIDE the ref token so a human skimming the delegation knows what
        the cached context is, without paying for the full blob.
        """
        for line in text.splitlines():
            line = line.strip()
            if line:
                return (line[:max_chars] + "…") if len(line) > max_chars else line
        return "(empty context)"

    def _key_of(self, ref_or_text: str) -> str:
        if ref_or_text.startswith("@ctx:"):
            return ref_or_text.split(":", 1)[1]
        return self._digest(ref_or_text)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Orchestrator — Routing & Orchestration engine.
# ─────────────────────────────────────────────────────────────────────────────

class Orchestrator:
    """Compose and route work to any specialist with a single call.

    The CEO's core verb. ``delegate()`` takes the four RCCF inputs the user asked
    for — **Role · Context · Conditions · Tools** — plus the task and priority, and
    returns a fully-formed :class:`Delegation`: the paste-ready spawn block, the
    resolved cheapest-clearing route, and a cached context reference so shared
    context is billed once.

    Usage
    -----
        ceo = Orchestrator()
        d = ceo.delegate(
            role="backend-blade-engineer",
            prj="PRJ-SAKK",
            task="Implement POST /refunds per the OpenAPI contract",
            context="Refund flow frozen at Gate 3; idempotency-key required.",
            conditions=["coverage >= 90%", "migration has rollback"],
            tools=["Read", "Write", "Edit", "Bash"],
            priority="HIGH",
        )
        print(d.block)     # paste to spawn the agent
    """

    #: Default tool grant per broad role family — overridable per call.
    DEFAULT_TOOLS: dict[str, list[str]] = {
        "strategy":  ["Read", "Write", "WebSearch", "WebFetch"],
        "architecture": ["Read", "Write", "Bash", "WebSearch", "WebFetch"],
        "backend":   ["Read", "Write", "Edit", "Bash"],
        "frontend":  ["Read", "Write", "Edit", "Bash"],
        "mobile":    ["Read", "Write", "Edit", "Bash"],
        "quality":   ["Read", "Write", "Edit", "Bash"],
        "infra":     ["Read", "Write", "Edit", "Bash"],
    }

    def __init__(self, cache: Optional[PromptCache] = None):
        self.cache = cache or PromptCache()

    # -- routing -------------------------------------------------------------
    def resolve_route(self, role: str, priority: Optional[str] = None) -> Route:
        """Resolve the cheapest model·effort·caveman route for a role.

        Delegates to ``sofi_tools.routing`` (the machine-readable routing.yaml) when
        available; otherwise applies a conservative workhorse default. Priority
        ``CRITICAL`` bumps the dials up; ``LOW`` caps them.
        """
        if _SOFI is not None:
            try:
                from sofi_tools import routing  # type: ignore
                r = routing.route_for(role, priority)
                return Route(
                    role=r["role"], model=r["model"], model_id=r["model_id"],
                    tier=r["tier"], effort=r["effort"], caveman=r["caveman"],
                    gate=str(r["gate"]), budget=str(r["budget"]),
                    priority=r["priority"],
                )
            except KeyError:
                # Unknown role — fall through to default so delegation still works.
                pass
            except Exception:
                pass
        return Route(role=role, priority=(priority or "—").upper())

    # -- tool grant ----------------------------------------------------------
    def default_tools(self, role: str) -> list[str]:
        """Tool grant for an agent: the registry's explicit grant when known
        (company/nexus/registry.yaml `tools:`), else a room-family default from
        the id's room prefix (<roomcode>-<role>)."""
        if _SOFI is not None:
            try:
                from sofi_tools import registry as _reg  # type: ignore
                tools = _reg.agent(role).get("tools")
                if isinstance(tools, (list, tuple)) and tools:
                    return list(tools)
                if tools == "inherit":
                    return ["Read", "Grep", "Glob", "Write", "Edit", "Bash",
                            "WebSearch", "WebFetch"]
            except Exception:
                pass
        room = role.split("-", 1)[0] if "-" in role else ""
        family = {
            "str": "strategy", "res": "strategy", "dsn": "strategy",
            "arc": "architecture", "dat": "backend", "bck": "backend",
            "fnt": "frontend", "mob": "mobile", "sec": "quality",
            "qa": "quality", "ops": "infra", "obs": "infra",
        }.get(room)
        if family:
            return self.DEFAULT_TOOLS[family]
        return ["Read", "Write", "Edit", "Bash"]

    # -- the single-call delegator ------------------------------------------
    def delegate(
        self,
        role: str,
        prj: str,
        task: str,
        context: str = "",
        conditions: Optional[list[str]] = None,
        tools: Optional[list[str]] = None,
        priority: Optional[str] = None,
        expected: str = "",
    ) -> Delegation:
        """Build one RCCF delegation for a specialist — the CEO's single function call.

        Parameters
        ----------
        role : str        Canonical role key (see :data:`SPEC_PATH`).
        prj : str         PRJ-ID the work belongs to (isolation boundary).
        task : str        The 🎯 Command — what to do, imperative, one thought.
        context : str     The 📂 Context blob; cached and referenced by digest.
        conditions : list Guardrail lines the output MUST satisfy (gate bar).
        tools : list      Explicit tool grant; falls back to the role's tier family.
        priority : str    CRITICAL | HIGH | MEDIUM | LOW — bends the route dials.
        expected : str    The 📐 Format — the artifact the CEO expects back.

        Returns
        -------
        Delegation with a paste-ready ``.block`` and machine fields.
        """
        conditions = list(conditions or [])
        tools = list(tools or self.default_tools(role))
        route = self.resolve_route(role, priority)
        spec = SPEC_PATH.get(role, f"<find-spec-for-{role}>")

        # Token economy: cache the context blob and reference it by digest.
        cached = bool(context) and self.cache.has(context)
        context_ref = self.cache.store(context, label=f"{prj}:{role}") if context else "—"
        ctx_hint = self.cache.digest_line(context) if context else "(no extra context)"

        block = self._render_rccf(
            role=role, prj=prj, task=task, spec=spec, route=route,
            conditions=conditions, tools=tools, context_ref=context_ref,
            ctx_hint=ctx_hint, expected=expected, cached=cached,
        )
        return Delegation(
            role=role, prj=prj, task=task, route=route, conditions=conditions,
            tools=tools, context_ref=context_ref, block=block, cached=cached,
        )

    # -- RCCF renderer -------------------------------------------------------
    @staticmethod
    def _render_rccf(
        role: str, prj: str, task: str, spec: str, route: Route,
        conditions: list[str], tools: list[str], context_ref: str,
        ctx_hint: str, expected: str, cached: bool,
    ) -> str:
        """Render the 4-part RCCF spawn block (🎭 Role · 📂 Context · 🎯 Command · 📐 Format)."""
        cond_lines = "\n".join(f"  - {c}" for c in conditions) or "  - (gate bar per spec)"
        tool_line = ", ".join(tools)
        cache_note = " (reused from cache — context NOT re-sent)" if cached else ""
        return f"""\
🎭 Role
You are {role}. Project: {prj}. Route: {route.model} · {route.effort} · {route.caveman} ({route.tier} {route.model_id}).
Spec + Operating Prompt: {spec} — read it before acting.

📂 Context{cache_note}
BEFORE acting, orient (never blind):
  - company/constitution/00-operating-system.md
  - projects/{prj}/_context/STATE.md   (note branch + head_sha)
  - projects/{prj}/_context/HANDOFFS.md (your ticket)
  - projects/{prj}/_context/CONTEXT.md
Extra context: {context_ref} — {ctx_hint}

🎯 Command
{task}

📐 Format (conditions the output MUST satisfy — CEO gates on these)
{cond_lines}
Allowed tools: {tool_line}
Expected artifact: {expected or '(per spec / ticket)'}

AFTER: write artifact → sofi checkpoint {prj} "<type>: ..." → append CONTEXT.md
(+DECISIONS.md if irreversible) → update STATE.md (head_sha) → write next ticket in HANDOFFS.md."""


# ─────────────────────────────────────────────────────────────────────────────
# 4. ProjectInspector — Automated Project Inspection engine.
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class FileEntry:
    """One row of the project tree matrix."""
    path: str            # repo-relative
    size: int            # bytes
    kind: str            # code | config | env | doc | data | other
    lang: str = ""       # php, py, dart, vue, js, yaml, ...
    sensitive: bool = False


@dataclass
class HealthReport:
    """The fast Health Check result — status, stack, gaps, smells, leaks."""
    root: str
    file_count: int
    total_bytes: int
    by_kind: dict[str, int]
    by_lang: dict[str, int]
    stack: list[str]
    findings: list[str]        # gaps / smells / errors, most severe first
    secret_hits: list[str]     # file:line of likely secret leaks (redacted)
    scanned_files: int
    skipped_dirs: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def render(self) -> str:
        """Terse, human-readable report — *big brain small mouth*."""
        lines = [
            f"🩺 Health Check — {self.root}",
            f"   files {self.file_count} · {self._h(self.total_bytes)} · "
            f"scanned {self.scanned_files} · skipped-dirs {self.skipped_dirs}",
            f"   stack: {', '.join(self.stack) or '(unknown)'}",
            f"   kinds: {self._fmt(self.by_kind)}",
            f"   langs: {self._fmt(self.by_lang)}",
        ]
        if self.secret_hits:
            lines.append(f"   🔴 possible secrets ({len(self.secret_hits)}):")
            lines += [f"      - {h}" for h in self.secret_hits[:12]]
            if len(self.secret_hits) > 12:
                lines.append(f"      … +{len(self.secret_hits) - 12} more")
        if self.findings:
            lines.append("   findings (worst first):")
            lines += [f"      {i+1}. {f}" for i, f in enumerate(self.findings)]
        else:
            lines.append("   findings: none — structure looks clean ✅")
        return "\n".join(lines)

    @staticmethod
    def _fmt(d: dict[str, int]) -> str:
        return ", ".join(f"{k}:{v}" for k, v in sorted(d.items(), key=lambda x: -x[1])) or "—"

    @staticmethod
    def _h(n: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if n < 1024:
                return f"{n:.0f}{unit}"
            n /= 1024
        return f"{n:.0f}TB"


class ProjectInspector:
    """Scan a project tree, read the files that matter, emit a Health Check.

    The CEO's eyes. It walks a directory while pruning the noise
    (``node_modules`` / ``vendor`` / ``.git`` / build caches) so the data handed to
    an LLM is small and relevant, then reports stack, structural gaps, and likely
    secret leaks.

    Usage
    -----
        insp = ProjectInspector()
        report = insp.health_check("PRJ-SAKK")   # PRJ-ID or a path
        print(report.render())
        matrix = insp.scan_tree("PRJ-SAKK")       # list[FileEntry]
    """

    #: Directories pruned entirely — never worth an LLM's tokens.
    IGNORE_DIRS = {
        "node_modules", "vendor", ".git", ".hg", ".svn", "dist", "build",
        ".next", ".nuxt", ".venv", "venv", "__pycache__", ".pytest_cache",
        ".idea", ".vscode", "coverage", ".cache", "storage", "bootstrap",
        ".dart_tool", "Pods", ".gradle", "target", "out", "tmp", ".terraform",
    }
    #: File globs skipped (binaries, locks, maps — bulk with no reasoning value).
    IGNORE_FILES = {
        "*.lock", "*.min.js", "*.min.css", "*.map", "*.png", "*.jpg", "*.jpeg",
        "*.gif", "*.webp", "*.ico", "*.svg", "*.pdf", "*.zip", "*.gz", "*.tar",
        "*.mp4", "*.mov", "*.woff", "*.woff2", "*.ttf", "*.eot", "*.class",
        "*.pyc", "*.so", "*.o", "*.a", "*.jar", "*.apk", "*.keystore",
    }
    #: Files always read closely — the load-bearing / sensitive ones.
    SENSITIVE_GLOBS = {
        ".env", ".env.*", "*.env", "config/*.php", "config/*.yaml", "config/*.yml",
        "settings.py", "settings.*.py", "application.yml", "application.properties",
        "docker-compose*.yml", "Dockerfile*", "*.tf", "*.pem", "*.key", "id_rsa*",
        "credentials*", "secrets*", "*.p12", "*.jks",
    }
    #: Extension → (kind, language).
    EXT_MAP = {
        ".php": ("code", "php"), ".py": ("code", "python"), ".dart": ("code", "dart"),
        ".vue": ("code", "vue"), ".js": ("code", "js"), ".ts": ("code", "ts"),
        ".jsx": ("code", "js"), ".tsx": ("code", "ts"), ".go": ("code", "go"),
        ".rb": ("code", "ruby"), ".java": ("code", "java"), ".kt": ("code", "kotlin"),
        ".rs": ("code", "rust"), ".sh": ("code", "shell"), ".sql": ("code", "sql"),
        ".blade.php": ("code", "blade"),
        ".yaml": ("config", "yaml"), ".yml": ("config", "yaml"),
        ".json": ("config", "json"), ".toml": ("config", "toml"),
        ".ini": ("config", "ini"), ".xml": ("config", "xml"),
        ".env": ("env", "env"),
        ".md": ("doc", "markdown"), ".txt": ("doc", "text"), ".rst": ("doc", "rst"),
        ".csv": ("data", "csv"),
    }
    #: Regexes that flag a likely committed secret (value redacted in output).
    SECRET_PATTERNS = [
        ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
        ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
        ("generic_secret", re.compile(
            r"(?i)(?:api[_-]?key|secret|password|passwd|token|bearer)\s*[:=]\s*"
            r"['\"]?([A-Za-z0-9/\+_\-]{16,})['\"]?")),
        ("slack_token", re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,}")),
        ("google_api", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
        ("stripe_live", re.compile(r"sk_live_[0-9A-Za-z]{16,}")),
    ]
    #: Public example/doc key VALUES that must NOT be flagged (known false positives).
    SECRET_ALLOWLIST = {"AKIAIOSFODNN7EXAMPLE"}
    #: Whole files skipped by BASENAME — not real leaks:
    #:   * secret-*scanners* whose source contains the very patterns they detect,
    #:   * public client configs that ship inside the app by design.
    #: Note: only these exact filenames — the enclosing secrets/ dir is still scanned.
    SECRET_ALLOW_FILES = {
        "pre-commit-hook.sh", "gitleaks.toml", ".gitleaks.toml", "trufflehog.yaml",
        "google-services.json", "GoogleService-Info.plist",
    }
    #: Languages treated as source code — a generic secret here must be a quoted
    #: literal; an unquoted match is a variable reference (e.g. `password: ctrl.text`).
    CODE_LANGS = {
        "php", "python", "dart", "vue", "js", "ts", "go", "ruby", "java",
        "kotlin", "rust", "shell", "sql", "blade",
    }

    def __init__(self, max_file_bytes: int = 512 * 1024):
        #: Files larger than this are catalogued but not content-scanned.
        self.max_file_bytes = max_file_bytes

    # -- tree walk -----------------------------------------------------------
    def scan_tree(self, target: str) -> list[FileEntry]:
        """Walk the project and return the filtered file matrix (list[FileEntry]).

        Prunes :attr:`IGNORE_DIRS` in-place (never descends them) and skips
        :attr:`IGNORE_FILES`, so the returned matrix is the reasoning-worthy subset.
        """
        root = _project_dir(target)
        if not root.exists():
            raise FileNotFoundError(f"no such project or path: {target}")
        entries: list[FileEntry] = []
        for dirpath, dirnames, filenames in os.walk(root):
            # Prune ignored dirs BEFORE descending (this is the token saver).
            dirnames[:] = [d for d in dirnames if d not in self.IGNORE_DIRS
                           and not d.startswith(".") or d in {".env"}]
            for fn in filenames:
                if any(fnmatch.fnmatch(fn, g) for g in self.IGNORE_FILES):
                    continue
                full = Path(dirpath) / fn
                try:
                    size = full.stat().st_size
                except OSError:
                    continue
                kind, lang = self._classify(fn)
                entries.append(FileEntry(
                    path=str(full.relative_to(root)),
                    size=size, kind=kind, lang=lang,
                    sensitive=self._is_sensitive(str(full.relative_to(root)), fn),
                ))
        return entries

    def read_sensitive(self, target: str, limit: int = 40) -> dict[str, str]:
        """Return {relpath: content} for the sensitive/load-bearing files.

        These are the files the CEO wants an LLM to actually read (env, config,
        infra manifests). Content over :attr:`max_file_bytes` is truncated with a
        marker so a single huge file can't blow the budget.
        """
        root = _project_dir(target)
        out: dict[str, str] = {}
        for e in self.scan_tree(target):
            if not e.sensitive or len(out) >= limit:
                continue
            full = root / e.path
            try:
                if e.size > self.max_file_bytes:
                    text = full.read_text(encoding="utf-8", errors="replace")[:self.max_file_bytes]
                    text += f"\n… [truncated at {self.max_file_bytes} bytes]"
                else:
                    text = full.read_text(encoding="utf-8", errors="replace")
                out[e.path] = text
            except Exception as ex:
                out[e.path] = f"[unreadable: {ex}]"
        return out

    # -- health check --------------------------------------------------------
    def health_check(self, target: str) -> HealthReport:
        """Produce the fast Health Check report for a project or path.

        Aggregates the tree matrix into counts/stack, scans code+config for secret
        leaks and structural gaps, and returns a :class:`HealthReport` (call
        ``.render()`` for the terse text or ``.to_dict()`` for JSON).
        """
        root = _project_dir(target)
        entries = self.scan_tree(target)
        by_kind: dict[str, int] = {}
        by_lang: dict[str, int] = {}
        total = 0
        skipped_dirs = self._count_pruned(root)
        for e in entries:
            by_kind[e.kind] = by_kind.get(e.kind, 0) + 1
            if e.lang:
                by_lang[e.lang] = by_lang.get(e.lang, 0) + 1
            total += e.size

        secret_hits = self._scan_secrets(root, entries)
        findings = self._structural_findings(root, entries, by_lang, secret_hits)
        stack = self._detect_stack(root, entries, by_lang)

        return HealthReport(
            root=str(root), file_count=len(entries), total_bytes=total,
            by_kind=by_kind, by_lang=by_lang, stack=stack, findings=findings,
            secret_hits=secret_hits, scanned_files=len(entries),
            skipped_dirs=skipped_dirs,
        )

    # -- helpers -------------------------------------------------------------
    def _classify(self, fn: str) -> tuple[str, str]:
        low = fn.lower()
        if low.endswith(".blade.php"):
            return self.EXT_MAP[".blade.php"]
        if low == ".env" or low.startswith(".env"):
            return ("env", "env")
        ext = "." + low.split(".")[-1] if "." in low else ""
        return self.EXT_MAP.get(ext, ("other", ""))

    def _is_sensitive(self, relpath: str, fn: str) -> bool:
        for g in self.SENSITIVE_GLOBS:
            if fnmatch.fnmatch(fn, g) or fnmatch.fnmatch(relpath, g):
                return True
        return False

    def _count_pruned(self, root: Path) -> int:
        n = 0
        for dirpath, dirnames, _ in os.walk(root):
            n += sum(1 for d in dirnames if d in self.IGNORE_DIRS)
            dirnames[:] = [d for d in dirnames if d not in self.IGNORE_DIRS]
        return n

    def _scan_secrets(self, root: Path, entries: list[FileEntry]) -> list[str]:
        """Scan text files for likely secrets; return redacted 'file:line (kind)' hits."""
        hits: list[str] = []
        for e in entries:
            if e.kind in {"other", "data"} or e.size > self.max_file_bytes:
                continue
            # Skip whole-file allowlist (scanners' own patterns, public client config).
            if e.path.rsplit("/", 1)[-1] in self.SECRET_ALLOW_FILES:
                continue
            full = root / e.path
            try:
                text = full.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            is_code = e.lang in self.CODE_LANGS
            for lineno, line in enumerate(text.splitlines(), 1):
                if any(a in line for a in self.SECRET_ALLOWLIST):
                    continue
                for name, pat in self.SECRET_PATTERNS:
                    m = pat.search(line)
                    if not m:
                        continue
                    # Skip obvious placeholders / example values.
                    if re.search(r"(?i)example|changeme|your[_-]?|xxxx|placeholder|\bnull\b", line):
                        break
                    if name == "generic_secret" and m.lastindex:
                        val = m.group(1)
                        # A URL / route path is not a credential (a var named
                        # `forgotPassword = '/auth/forgot-password'` is an endpoint).
                        if val.startswith("/") or re.match(r"\w+://", val):
                            break
                        # In source code, a generic secret must be a QUOTED literal;
                        # an unquoted capture is a variable reference, not a secret.
                        if is_code:
                            s = m.start(1)
                            if not (s > 0 and line[s - 1] in "'\""):
                                break
                    hits.append(f"{e.path}:{lineno} ({name})")
                    break
        return hits

    def _structural_findings(
        self, root: Path, entries: list[FileEntry],
        by_lang: dict[str, int], secret_hits: list[str],
    ) -> list[str]:
        """Cheap heuristics for gaps/smells — ranked most-severe first."""
        f: list[str] = []
        names = {e.path for e in entries}
        top = {p.split("/")[0] for p in names}

        if secret_hits:
            f.append(f"🔴 {len(secret_hits)} possible secret(s) in tracked files — rotate + gitignore.")

        # Committed .env is a leak risk.
        if any(e.kind == "env" and not e.path.endswith(".example") for e in entries):
            f.append("🔴 a real .env is present in the tree — confirm it is git-ignored, never committed.")

        # No tests.
        has_tests = any(re.search(r"(^|/)(tests?|__tests__|spec)(/|$)", p, re.I) for p in names)
        if not has_tests and by_lang:
            f.append("🟠 no test/ directory detected — coverage bar (<90% = rejected) at risk.")

        # No README / docs.
        if not any(p.lower().startswith("readme") for p in names):
            f.append("🟡 no README at root — onboarding + intent undocumented.")

        # Version control — only flag a standalone app root that has no git anywhere
        # up its parent chain (a sub-directory of a tracked repo is fine).
        looks_like_app = bool({"composer.json", "package.json", "pubspec.yaml",
                               "pyproject.toml", "go.mod"} & names)
        if looks_like_app and not self._in_git_tree(root):
            f.append("🟠 not under git — 'git is the spine'; no checkpoint/rollback possible.")

        # Laravel-specific: migrations without obvious rollback.
        migs = [e.path for e in entries if "/migrations/" in e.path and e.lang == "php"]
        if migs:
            missing_down = self._migrations_missing_down(root, migs)
            if missing_down:
                f.append(f"🔴 {len(missing_down)} migration(s) lack a down()/rollback — 'migration without rollback = rejected'.")

        # Dependency manifest but no lockfile committed context.
        if "composer.json" in names and "composer.lock" not in names:
            f.append("🟡 composer.json without composer.lock in-tree — non-reproducible installs.")
        if "package.json" in names and not any(p in names for p in ("package-lock.json", "yarn.lock", "pnpm-lock.yaml")):
            f.append("🟡 package.json without a lockfile — non-reproducible installs.")

        # Very large single files (maintainability smell).
        big = [(e.path, e.size) for e in entries if e.kind == "code" and e.size > 80 * 1024]
        for p, s in sorted(big, key=lambda x: -x[1])[:3]:
            f.append(f"🟡 large code file {p} ({HealthReport._h(s)}) — consider splitting.")

        return f

    def _in_git_tree(self, root: Path) -> bool:
        """True if root or any parent contains a .git — no subprocess."""
        for d in (root, *root.parents):
            if (d / ".git").exists():
                return True
        return False

    def _migrations_missing_down(self, root: Path, migs: list[str]) -> list[str]:
        out = []
        for p in migs:
            try:
                text = (root / p).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if "function down" not in text and "public function down" not in text:
                out.append(p)
        return out

    def _detect_stack(
        self, root: Path, entries: list[FileEntry], by_lang: dict[str, int],
    ) -> list[str]:
        """Infer the tech stack from manifest files + dominant languages."""
        names = {e.path for e in entries}
        stack: list[str] = []
        if "composer.json" in names or by_lang.get("php"):
            stack.append("Laravel/PHP" if any("artisan" in p or "laravel" in p.lower() for p in names)
                         or (root / "artisan").exists() else "PHP")
        if by_lang.get("blade"):
            stack.append("Blade")
        if by_lang.get("vue"):
            stack.append("Vue")
        if "pubspec.yaml" in names or by_lang.get("dart"):
            stack.append("Flutter/Dart")
        if "package.json" in names and "Vue" not in stack and by_lang.get("js", 0) + by_lang.get("ts", 0):
            stack.append("Node/JS")
        if by_lang.get("python"):
            stack.append("Python")
        if any(e.path.endswith(".tf") for e in entries):
            stack.append("Terraform")
        return stack


# ─────────────────────────────────────────────────────────────────────────────
# 5. ComplianceEngine — Guardrails & Conditions engine.
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Condition:
    """One declarative guardrail checked against an agent's output.

    Exactly one predicate field is set. ``hard=True`` conditions block acceptance;
    ``hard=False`` are advisory warnings that still surface in the verdict.
    """
    name: str
    kind: str                       # contains | not_contains | regex | not_regex |
                                    # min_len | file_exists | json_valid | custom
    value: Any = None
    hard: bool = True
    _fn: Optional[Callable[[str], bool]] = None   # for kind="custom"


@dataclass
class ComplianceResult:
    """Verdict of a compliance check — per-condition results + overall pass."""
    passed: bool                    # all HARD conditions satisfied
    checks: list[dict[str, Any]]    # [{name, kind, hard, ok, detail}]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def render(self) -> str:
        head = "✅ COMPLIANT — accept" if self.passed else "🔴 NON-COMPLIANT — reject / return"
        lines = [head]
        for c in self.checks:
            mark = "✓" if c["ok"] else ("✗" if c["hard"] else "⚠")
            sev = "" if c["hard"] else " (advisory)"
            lines.append(f"  {mark} {c['name']}{sev}: {c['detail']}")
        return "\n".join(lines)


class ComplianceEngine:
    """Check an agent's output against declared conditions BEFORE the CEO accepts it.

    The governance gate. The CEO declares what "done" means as a list of
    :class:`Condition`s (or a plain rules dict / JSON), then runs ``check()`` on the
    delivered artifact. Any failed **hard** condition means the CEO returns the work
    instead of advancing the gate — so a gate bar cannot be silently skipped.

    Usage
    -----
        eng = ComplianceEngine()
        conds = eng.from_rules({
            "must_contain": ["public function down"],   # migration rollback present
            "must_not_contain": ["dd(", "var_dump("],   # no debug leftovers
            "regex": [r"class\\s+\\w+"],
            "min_len": 50,
        })
        verdict = eng.check(delivered_code, conds)
        print(verdict.render())
        if not verdict.passed: ...  # return to agent
    """

    # -- build conditions ----------------------------------------------------
    def from_rules(self, rules: dict[str, Any]) -> list[Condition]:
        """Translate a plain rules dict (or parsed JSON) into Condition objects.

        Recognised keys: ``must_contain`` (list), ``must_not_contain`` (list),
        ``regex`` (list), ``not_regex`` (list), ``min_len`` (int),
        ``file_exists`` (list of paths), ``json_valid`` (bool),
        ``soft`` (dict of the same shape, whose conditions are advisory).
        """
        conds: list[Condition] = []
        conds += self._expand(rules, hard=True)
        soft = rules.get("soft")
        if isinstance(soft, dict):
            conds += self._expand(soft, hard=False)
        return conds

    def _expand(self, rules: dict[str, Any], hard: bool) -> list[Condition]:
        out: list[Condition] = []
        for token in rules.get("must_contain", []) or []:
            out.append(Condition(f"contains:{token}", "contains", token, hard))
        for token in rules.get("must_not_contain", []) or []:
            out.append(Condition(f"absent:{token}", "not_contains", token, hard))
        for pat in rules.get("regex", []) or []:
            out.append(Condition(f"regex:{pat}", "regex", pat, hard))
        for pat in rules.get("not_regex", []) or []:
            out.append(Condition(f"not_regex:{pat}", "not_regex", pat, hard))
        if "min_len" in rules:
            out.append(Condition("min_len", "min_len", int(rules["min_len"]), hard))
        for path in rules.get("file_exists", []) or []:
            out.append(Condition(f"file_exists:{path}", "file_exists", path, hard))
        if rules.get("json_valid"):
            out.append(Condition("json_valid", "json_valid", True, hard))
        return out

    def condition(self, name: str, fn: Callable[[str], bool], hard: bool = True) -> Condition:
        """Wrap an arbitrary predicate as a custom Condition (returns True = pass)."""
        return Condition(name, "custom", None, hard, _fn=fn)

    # -- run the check -------------------------------------------------------
    def check(self, output: str, conditions: Iterable[Condition],
              base_dir: Optional[Path] = None) -> ComplianceResult:
        """Evaluate every condition against ``output`` and return a verdict.

        ``base_dir`` roots any ``file_exists`` checks (defaults to cwd). The overall
        ``passed`` is True only when every **hard** condition is satisfied; advisory
        failures are reported but never block.
        """
        base_dir = base_dir or Path.cwd()
        checks: list[dict[str, Any]] = []
        passed = True
        for c in conditions:
            ok, detail = self._eval(c, output, base_dir)
            if c.hard and not ok:
                passed = False
            checks.append({"name": c.name, "kind": c.kind, "hard": c.hard,
                           "ok": ok, "detail": detail})
        return ComplianceResult(passed=passed, checks=checks)

    def _eval(self, c: Condition, output: str, base_dir: Path) -> tuple[bool, str]:
        try:
            if c.kind == "contains":
                ok = str(c.value) in output
                return ok, "found" if ok else f"missing required substring '{c.value}'"
            if c.kind == "not_contains":
                ok = str(c.value) not in output
                return ok, "absent" if ok else f"forbidden substring '{c.value}' present"
            if c.kind == "regex":
                ok = re.search(str(c.value), output) is not None
                return ok, "matched" if ok else f"pattern /{c.value}/ not found"
            if c.kind == "not_regex":
                ok = re.search(str(c.value), output) is None
                return ok, "clean" if ok else f"forbidden pattern /{c.value}/ present"
            if c.kind == "min_len":
                ok = len(output) >= int(c.value)
                return ok, f"len={len(output)} >= {c.value}" if ok else f"len={len(output)} < {c.value}"
            if c.kind == "file_exists":
                ok = (base_dir / str(c.value)).exists()
                return ok, "exists" if ok else f"expected file '{c.value}' not found"
            if c.kind == "json_valid":
                json.loads(output)
                return True, "valid JSON"
            if c.kind == "custom" and c._fn is not None:
                ok = bool(c._fn(output))
                return ok, "predicate passed" if ok else "predicate failed"
        except json.JSONDecodeError as ex:
            return False, f"invalid JSON: {ex}"
        except Exception as ex:
            return False, f"check error: {ex}"
        return False, "unknown condition kind"


# ─────────────────────────────────────────────────────────────────────────────
# 6. CLI — one dispatcher so the CEO drives all three engines from the shell.
# ─────────────────────────────────────────────────────────────────────────────

def _cmd_delegate(a: argparse.Namespace) -> int:
    ceo = Orchestrator()
    d = ceo.delegate(
        role=a.role, prj=a.prj, task=a.task or "(see ticket)",
        context=a.context or "", priority=a.priority,
        conditions=a.condition or [], tools=a.tool or None,
        expected=a.expected or "",
    )
    if a.json:
        print(json.dumps(d.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(d.block)
    return 0


def _cmd_inspect(a: argparse.Namespace) -> int:
    insp = ProjectInspector()
    matrix = insp.scan_tree(a.target)
    if a.json:
        print(json.dumps([asdict(e) for e in matrix], ensure_ascii=False, indent=2))
    else:
        print(f"📂 {len(matrix)} files (filtered) in {_project_dir(a.target)}")
        for e in sorted(matrix, key=lambda x: (-x.sensitive, x.path))[:200]:
            flag = "🔑" if e.sensitive else "  "
            print(f"  {flag} {e.path:<60} {e.kind:<7} {e.lang}")
    return 0


def _cmd_health(a: argparse.Namespace) -> int:
    insp = ProjectInspector()
    report = insp.health_check(a.target)
    if a.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(report.render())
    return 0 if not report.secret_hits else 1


def _cmd_comply(a: argparse.Namespace) -> int:
    eng = ComplianceEngine()
    rules = json.loads(Path(a.rules).read_text(encoding="utf-8"))
    conds = eng.from_rules(rules)
    output = Path(a.output).read_text(encoding="utf-8") if Path(a.output).exists() else a.output
    verdict = eng.check(output, conds, base_dir=Path(a.output).resolve().parent
                        if Path(a.output).exists() else Path.cwd())
    if a.json:
        print(json.dumps(verdict.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(verdict.render())
    return 0 if verdict.passed else 2


def _cmd_routes(a: argparse.Namespace) -> int:
    ceo = Orchestrator()
    roles = sorted(SPEC_PATH.keys())
    if _SOFI is not None:
        try:
            from sofi_tools import routing  # type: ignore
            roles = sorted(set(roles) | set(routing.all_roles()))
        except Exception:
            pass
    for role in roles:
        print(f"{role:<34} {ceo.resolve_route(role).one_line()}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the CEO console CLI (subcommands: delegate/inspect/health/comply/routes)."""
    p = argparse.ArgumentParser(
        prog="ceo_toolkit",
        description="SOFI CEO console — route work, inspect projects, gate outputs.")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("delegate", help="build one RCCF delegation block")
    d.add_argument("role")
    d.add_argument("--prj", required=True)
    d.add_argument("--task", default="")
    d.add_argument("--context", default="")
    d.add_argument("--expected", default="")
    d.add_argument("--priority", default=None,
                   choices=["CRITICAL", "HIGH", "MEDIUM", "LOW"])
    d.add_argument("--condition", action="append", help="repeatable gate condition")
    d.add_argument("--tool", action="append", help="repeatable tool grant")
    d.add_argument("--json", action="store_true")
    d.set_defaults(func=_cmd_delegate)

    i = sub.add_parser("inspect", help="print the filtered project file matrix")
    i.add_argument("target", help="PRJ-ID or path")
    i.add_argument("--json", action="store_true")
    i.set_defaults(func=_cmd_inspect)

    h = sub.add_parser("health", help="fast Health Check report")
    h.add_argument("target", help="PRJ-ID or path")
    h.add_argument("--json", action="store_true")
    h.set_defaults(func=_cmd_health)

    c = sub.add_parser("comply", help="check an output file against a rules.json")
    c.add_argument("output", help="artifact file (or literal string)")
    c.add_argument("--rules", required=True, help="path to rules.json")
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=_cmd_comply)

    r = sub.add_parser("routes", help="dump the resolved route table")
    r.set_defaults(func=_cmd_routes)
    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
