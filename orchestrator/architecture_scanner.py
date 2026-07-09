#!/usr/bin/env python3
"""architecture_scanner.py — context pruning.

Reads the (optional) Laravel and Flutter code trees and produces a COMPACT,
token-bounded picture of the existing architecture: tables + columns, api
routes, Flutter widgets/models. It then filters that down to only the items
whose names intersect the refined payload — so the code-generation step gets a
tight, relevant context instead of the whole repo.

Everything degrades gracefully: a missing or unreadable path yields
``available: false`` and empty lists, never a crash.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, List, Optional

# --------------------------------------------------------------------------- #
# Base dir + limits
# --------------------------------------------------------------------------- #
BASE: Path = Path(os.environ.get("SOFI_HOME") or Path(__file__).resolve().parent)

MAX_ITEMS = 50  # cap per list to prune tokens
MAX_FILES_SCAN = 500  # never walk an unbounded tree
MAX_FILE_BYTES = 512_000  # skip absurdly large files


# --------------------------------------------------------------------------- #
# rich console with a graceful fallback shim
# --------------------------------------------------------------------------- #
_MARKUP_RE = re.compile(r"\[/?[a-zA-Z0-9 #_.,=-]+\]")


class _ConsoleShim:
    @staticmethod
    def print(*args: object, **_kwargs: object) -> None:
        print(*[_MARKUP_RE.sub("", str(a)) for a in args])


try:  # pragma: no cover
    from rich.console import Console as _RichConsole

    _console: object = _RichConsole()
except Exception:  # pragma: no cover
    _console = _ConsoleShim()


# --------------------------------------------------------------------------- #
# Regexes for Laravel migration / route extraction
# --------------------------------------------------------------------------- #
_SCHEMA_CREATE_RE = re.compile(r"Schema::create\(\s*['\"]([a-zA-Z0-9_]+)['\"]")
_SCHEMA_TABLE_RE = re.compile(r"Schema::table\(\s*['\"]([a-zA-Z0-9_]+)['\"]")
# ->string('col'), ->integer('col'), ->boolean('col'), ->text('col'), etc.
_COLUMN_RE = re.compile(
    r"->\s*(string|integer|bigInteger|unsignedBigInteger|boolean|text|"
    r"longText|date|dateTime|timestamp|float|double|decimal|json|uuid|char|"
    r"tinyInteger|smallInteger|mediumText|enum|foreignId)\s*\(\s*['\"]([a-zA-Z0-9_]+)['\"]"
)
_ROUTE_RE = re.compile(
    r"Route::\s*(get|post|put|patch|delete|any|match|apiResource|resource)\s*\(\s*['\"]([^'\"]+)['\"]"
)


class ArchitectureScanner:
    """Scans Laravel + Flutter trees and prunes to a payload-relevant context."""

    def __init__(
        self, laravel_path: Optional[str], flutter_path: Optional[str]
    ) -> None:
        self.laravel_path: Optional[Path] = Path(laravel_path) if laravel_path else None
        self.flutter_path: Optional[Path] = Path(flutter_path) if flutter_path else None

    # -- public API --------------------------------------------------------- #
    def scan(self, payload: Dict[str, object]) -> Dict[str, object]:
        laravel = self._scan_laravel()
        flutter = self._scan_flutter()
        relevant = self._prune(payload, laravel, flutter)
        return {"laravel": laravel, "flutter": flutter, "relevant": relevant}

    # -- Laravel ------------------------------------------------------------ #
    def _scan_laravel(self) -> Dict[str, object]:
        result: Dict[str, object] = {"available": False, "tables": [], "routes": []}
        path = self.laravel_path
        if path is None:
            return result
        try:
            if not path.is_dir():
                return result
        except OSError:
            return result

        result["available"] = True
        result["tables"] = self._scan_migrations(path / "database" / "migrations")
        result["routes"] = self._scan_routes(path / "routes" / "api.php")
        return result

    def _scan_migrations(self, migrations_dir: Path) -> List[Dict[str, object]]:
        tables: Dict[str, Dict[str, object]] = {}
        try:
            if not migrations_dir.is_dir():
                return []
            files = sorted(migrations_dir.glob("*.php"))
        except OSError:
            return []

        for php in files[:MAX_FILES_SCAN]:
            content = self._read_text(php)
            if content is None:
                continue
            create_tables = _SCHEMA_CREATE_RE.findall(content)
            alter_tables = _SCHEMA_TABLE_RE.findall(content)
            columns = [name for _type, name in _COLUMN_RE.findall(content)]

            target_tables = create_tables or alter_tables
            if not target_tables:
                continue
            # Attribute all found columns to the (usually single) table in the file.
            primary = target_tables[0]
            entry = tables.setdefault(primary, {"table": primary, "fields": []})
            existing = {f for f in entry["fields"]}  # type: ignore[assignment]
            for col in columns:
                if col not in existing:
                    entry["fields"].append(col)  # type: ignore[union-attr]
                    existing.add(col)

        out: List[Dict[str, object]] = []
        for entry in list(tables.values())[:MAX_ITEMS]:
            entry["fields"] = entry["fields"][:MAX_ITEMS]  # type: ignore[index]
            out.append(entry)
        return out

    def _scan_routes(self, routes_file: Path) -> List[str]:
        content = self._read_text(routes_file)
        if content is None:
            return []
        routes: List[str] = []
        seen: set = set()
        for verb, uri in _ROUTE_RE.findall(content):
            label = f"{verb.upper()} {uri}"
            if label not in seen:
                routes.append(label)
                seen.add(label)
            if len(routes) >= MAX_ITEMS:
                break
        return routes

    # -- Flutter ------------------------------------------------------------ #
    def _scan_flutter(self) -> Dict[str, object]:
        result: Dict[str, object] = {"available": False, "widgets": [], "models": []}
        path = self.flutter_path
        if path is None:
            return result
        try:
            if not path.is_dir():
                return result
        except OSError:
            return result

        result["available"] = True
        lib = path / "lib"
        widgets: List[str] = []
        models: List[str] = []
        try:
            if lib.is_dir():
                dart_files = sorted(lib.rglob("*.dart"))
            else:
                dart_files = sorted(path.rglob("*.dart"))
        except OSError:
            dart_files = []

        for dart in dart_files[:MAX_FILES_SCAN]:
            try:
                stem = dart.stem
            except (OSError, ValueError):
                continue
            lower = stem.lower()
            if lower.endswith("_model") or lower.endswith("_dto") or lower.endswith("_entity"):
                if stem not in models:
                    models.append(stem)
            else:
                if stem not in widgets:
                    widgets.append(stem)

        result["widgets"] = widgets[:MAX_ITEMS]
        result["models"] = models[:MAX_ITEMS]
        return result

    # -- pruning ------------------------------------------------------------ #
    @staticmethod
    def _prune(
        payload: Dict[str, object],
        laravel: Dict[str, object],
        flutter: Dict[str, object],
    ) -> Dict[str, object]:
        wanted_tables = set()
        wanted_screens = set()

        for mut in payload.get("database_mutations", []) or []:
            if isinstance(mut, dict) and mut.get("table"):
                wanted_tables.add(str(mut["table"]).lower())
        for ui in payload.get("ui_changes", []) or []:
            if isinstance(ui, dict) and ui.get("screen"):
                wanted_screens.add(str(ui["screen"]).lower())

        def _name_matches(name: str, wanted: set) -> bool:
            low = name.lower()
            for w in wanted:
                token = w.replace("_screen", "").replace("_page", "")
                if low == w or (token and (token in low or low in token)):
                    return True
            return False

        rel_tables = [
            t for t in (laravel.get("tables") or [])
            if isinstance(t, dict) and str(t.get("table", "")).lower() in wanted_tables
        ][:MAX_ITEMS]

        rel_routes = [
            r for r in (laravel.get("routes") or [])
            if any(w in str(r).lower() for w in wanted_tables)
        ][:MAX_ITEMS]

        rel_widgets = [
            w for w in (flutter.get("widgets") or [])
            if _name_matches(str(w), wanted_screens)
        ][:MAX_ITEMS]

        rel_models = [
            m for m in (flutter.get("models") or [])
            if _name_matches(str(m), wanted_tables | wanted_screens)
        ][:MAX_ITEMS]

        return {
            "tables": rel_tables,
            "routes": rel_routes,
            "widgets": rel_widgets,
            "models": rel_models,
        }

    # -- IO helper ---------------------------------------------------------- #
    @staticmethod
    def _read_text(path: Path) -> Optional[str]:
        try:
            if not path.is_file():
                return None
            if path.stat().st_size > MAX_FILE_BYTES:
                return None
            return path.read_text(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            return None


# --------------------------------------------------------------------------- #
# Selftest (offline; builds a tmp fake app)
# --------------------------------------------------------------------------- #
def _selftest() -> bool:
    import tempfile
    import shutil

    ok = True
    tmp = Path(tempfile.mkdtemp(prefix="sofi_scanner_"))
    try:
        # Fake Laravel app.
        laravel = tmp / "laravel"
        mig = laravel / "database" / "migrations"
        mig.mkdir(parents=True, exist_ok=True)
        (mig / "2024_01_01_000000_create_users_table.php").write_text(
            "<?php\n"
            "use Illuminate\\Database\\Migrations\\Migration;\n"
            "return new class extends Migration {\n"
            "  public function up() {\n"
            "    Schema::create('users', function (Blueprint $table) {\n"
            "      $table->id();\n"
            "      $table->string('name');\n"
            "      $table->string('phone_number')->nullable();\n"
            "      $table->boolean('is_active')->default(true);\n"
            "    });\n"
            "  }\n"
            "};\n",
            encoding="utf-8",
        )
        routes = laravel / "routes"
        routes.mkdir(parents=True, exist_ok=True)
        (routes / "api.php").write_text(
            "<?php\n"
            "Route::get('/users', [UserController::class, 'index']);\n"
            "Route::post('/users', [UserController::class, 'store']);\n"
            "Route::get('/orders', [OrderController::class, 'index']);\n",
            encoding="utf-8",
        )

        # Fake Flutter app.
        flutter = tmp / "flutter"
        lib = flutter / "lib"
        lib.mkdir(parents=True, exist_ok=True)
        (lib / "profile_screen.dart").write_text("class ProfileScreen {}\n", encoding="utf-8")
        (lib / "home_screen.dart").write_text("class HomeScreen {}\n", encoding="utf-8")
        (lib / "user_model.dart").write_text("class UserModel {}\n", encoding="utf-8")

        payload = {
            "intent": "add phone_number",
            "target_stack": "Both",
            "database_mutations": [
                {"table": "users", "fields": [{"name": "phone_number", "type": "string"}]}
            ],
            "ui_changes": [{"screen": "profile_screen", "widgets": ["phone_field"]}],
        }

        scanner = ArchitectureScanner(str(laravel), str(flutter))
        ctx = scanner.scan(payload)

        assert ctx["laravel"]["available"] is True, "laravel must be available"
        tables = ctx["laravel"]["tables"]
        users = next((t for t in tables if t["table"] == "users"), None)
        assert users is not None, "users table must be discovered"
        assert "phone_number" in users["fields"], f"phone_number must be found, got {users['fields']}"
        assert any("users" in r.lower() for r in ctx["laravel"]["routes"]), "users routes must be found"

        assert ctx["flutter"]["available"] is True, "flutter must be available"
        assert "profile_screen" in ctx["flutter"]["widgets"], "profile_screen widget must be listed"
        assert "user_model" in ctx["flutter"]["models"], "user_model must be classified as model"

        # relevant picks up users + profile.
        rel = ctx["relevant"]
        assert any(t["table"] == "users" for t in rel["tables"]), "relevant must include users table"
        assert "profile_screen" in rel["widgets"], "relevant must include profile_screen"

        # Missing-path degradation.
        degraded = ArchitectureScanner(str(tmp / "nope"), None).scan(payload)
        assert degraded["laravel"]["available"] is False, "missing laravel must degrade"
        assert degraded["laravel"]["tables"] == [], "missing laravel must have no tables"
        assert degraded["flutter"]["available"] is False, "None flutter must degrade"
    except AssertionError as exc:
        ok = False
        _console.print(f"[red]assertion failed:[/red] {exc}")
    except Exception as exc:  # noqa: BLE001
        ok = False
        _console.print(f"[red]unexpected error:[/red] {exc}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    _console.print("[bold green]PASS[/bold green] architecture_scanner selftest" if ok else "[bold red]FAIL[/bold red] architecture_scanner selftest")
    return ok


if __name__ == "__main__":
    import sys

    sys.exit(0 if _selftest() else 1)
