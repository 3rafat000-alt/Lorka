"""SOFI tools — room manager.

Discovers every room tool module under the ``tools.rooms`` package, builds
registries of tool classes / rooms / self-test samples, and exposes a typed API
to list, fetch, run, and self-test tools.

Discovery is deliberately defensive: a broken or missing room module (import
error, malformed ``TOOLS``, bad tool class) is logged to stderr and *skipped* —
never fatal. Room modules may be partially present while they are built in
parallel, and the manager must keep working over whatever exists.

Contract (see ``tools/tool_base.py``): each ``tools/rooms/<mod>.py`` exposes
``TOOLS: list[type[Tool]]`` and ``SELFTEST_SAMPLES: dict[str, dict]`` mapping a
tool's ``name`` to a valid sample params dict.

Importing this module has no side effects beyond defining names — discovery only
runs when a :class:`RoomManager` is constructed (or ``discover()`` is called).
"""
from __future__ import annotations

import importlib
import pkgutil
import sys
from typing import Any, Dict, List, Optional, Type

from tools.tool_base import Tool, ToolResult

# Dotted path of the package that holds room tool modules.
ROOMS_PACKAGE: str = "tools.rooms"


def _log(msg: str) -> None:
    """Emit a non-fatal diagnostic to stderr (never stdout)."""
    print(f"[room_manager] {msg}", file=sys.stderr)


class RoomManager:
    """Discovers and orchestrates every room tool.

    Registries built by :meth:`discover`:
      * ``_by_name``   — tool ``name`` -> tool class
      * ``_by_room``   — room code -> sorted list of tool names
      * ``_samples``   — tool ``name`` -> self-test sample params
    """

    def __init__(self, discover: bool = True) -> None:
        self._by_name: Dict[str, Type[Tool]] = {}
        self._by_room: Dict[str, List[str]] = {}
        self._samples: Dict[str, Dict[str, Any]] = {}
        self._loaded: List[str] = []
        self._failed: List[str] = []
        if discover:
            self.discover()

    # -- discovery -------------------------------------------------------
    def discover(self) -> None:
        """Import every submodule of ``tools.rooms`` and register its tools.

        Idempotent: clears and rebuilds all registries. Any per-module failure is
        logged and skipped so a single broken module cannot break discovery.
        """
        self._by_name.clear()
        self._by_room.clear()
        self._samples.clear()
        self._loaded.clear()
        self._failed.clear()

        try:
            pkg = importlib.import_module(ROOMS_PACKAGE)
        except Exception as exc:  # package itself missing/broken -> nothing to do
            _log(f"cannot import package {ROOMS_PACKAGE!r}: {type(exc).__name__}: {exc}")
            return

        search_paths = list(getattr(pkg, "__path__", []) or [])
        for mod_info in pkgutil.iter_modules(search_paths):
            short = mod_info.name
            if short.startswith("_"):
                continue  # skip dunder/private helpers (e.g. __init__, _shared)
            full = f"{ROOMS_PACKAGE}.{short}"
            try:
                module = importlib.import_module(full)
            except Exception as exc:  # broken/missing module -> skip, never fatal
                self._failed.append(short)
                _log(f"skipped module {full!r}: {type(exc).__name__}: {exc}")
                continue
            self._register_module(short, module)

    def _register_module(self, short: str, module: Any) -> None:
        """Pull ``TOOLS`` / ``SELFTEST_SAMPLES`` from one module and register them."""
        tools = getattr(module, "TOOLS", None)
        samples = getattr(module, "SELFTEST_SAMPLES", None)
        if not isinstance(samples, dict):
            if samples is not None:
                _log(f"module {short!r}: SELFTEST_SAMPLES is not a dict — ignoring samples")
            samples = {}
        if not isinstance(tools, (list, tuple)):
            _log(f"module {short!r}: TOOLS missing or not a list — no tools registered")
            self._loaded.append(short)
            return

        registered = 0
        for entry in tools:
            if not (isinstance(entry, type) and issubclass(entry, Tool)):
                _log(f"module {short!r}: ignoring non-Tool entry {entry!r}")
                continue
            name = getattr(entry, "name", "") or ""
            if not isinstance(name, str) or not name:
                _log(f"module {short!r}: ignoring tool {entry.__name__} with empty name")
                continue
            if name in self._by_name:
                _log(f"module {short!r}: duplicate tool name {name!r} — keeping first")
                continue
            room = getattr(entry, "room", "") or ""
            if not isinstance(room, str):
                room = str(room)
            self._by_name[name] = entry
            self._by_room.setdefault(room, []).append(name)
            self._by_room[room].sort()
            sample = samples.get(name)
            if isinstance(sample, dict):
                self._samples[name] = sample
            elif sample is not None:
                _log(f"module {short!r}: sample for {name!r} is not a dict — ignoring")
            registered += 1

        self._loaded.append(short)
        if registered == 0:
            _log(f"module {short!r}: loaded but registered 0 tools")

    # -- typed API -------------------------------------------------------
    def rooms(self) -> List[str]:
        """Return every discovered room code, sorted."""
        return sorted(self._by_room.keys())

    def list_tools(self, room: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return ``Tool.spec()`` for every tool, or only those in ``room``.

        Results are sorted by tool name for deterministic output.
        """
        if room is None:
            names = sorted(self._by_name.keys())
        else:
            names = sorted(self._by_room.get(room, []))
        return [self._by_name[n].spec() for n in names]

    def get(self, name: str) -> Optional[Type[Tool]]:
        """Return the tool class registered under ``name`` (or ``None``)."""
        return self._by_name.get(name)

    def samples(self, name: str) -> Optional[Dict[str, Any]]:
        """Return a copy of the self-test sample params for ``name`` (or ``None``)."""
        sample = self._samples.get(name)
        return dict(sample) if sample is not None else None

    def run(self, name: str, params: Dict[str, Any]) -> ToolResult:
        """Instantiate the named tool and execute it with ``params``.

        Unknown name -> ``ToolResult(ok=False, error="unknown tool: <name>")``.
        Instantiation / execution errors are captured into a failed ToolResult;
        no exception escapes.
        """
        cls = self._by_name.get(name)
        if cls is None:
            return ToolResult(ok=False, error=f"unknown tool: {name}")
        try:
            return cls().execute(params)
        except Exception as exc:  # e.g. a tool whose __init__ raises
            return ToolResult(ok=False, error=f"{type(exc).__name__}: {exc}")

    def selftest(self) -> Dict[str, Any]:
        """Run every discovered tool against its self-test sample.

        Returns ``{"ok": bool, "total": N, "passed": M, "failures": [...]}`` where
        each failure is ``{"name": str, "error": str}``. A tool with no sample is
        counted as a failure so the gap is surfaced, not silently passed.
        """
        names = sorted(self._by_name.keys())
        total = len(names)
        passed = 0
        failures: List[Dict[str, str]] = []
        for name in names:
            sample = self._samples.get(name)
            if sample is None:
                failures.append({"name": name, "error": "no selftest sample"})
                continue
            result = self.run(name, sample)
            if result.ok:
                passed += 1
            else:
                failures.append({"name": name, "error": result.error or "unknown error"})
        return {
            "ok": len(failures) == 0,
            "total": total,
            "passed": passed,
            "failures": failures,
        }

    # -- introspection (non-contract convenience) ------------------------
    def loaded_modules(self) -> List[str]:
        """Room modules successfully imported (may still have registered 0 tools)."""
        return sorted(self._loaded)

    def failed_modules(self) -> List[str]:
        """Room modules that failed to import and were skipped."""
        return sorted(self._failed)
