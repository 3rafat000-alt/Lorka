"""BKD-05 — Backend (Laravel/PHP) room tools.

Deterministic code-generation capabilities the backend room reaches for:
  * bkd.make_migration    — a Laravel migration PHP file + publish schema to the SSoT.
  * bkd.make_api_resource — a JsonResource class + a thin controller stub.
  * bkd.run_checks        — reuse the `check` substrate to lint/analyse the Laravel app.

Every tool subclasses tools.tool_base.Tool and implements only run(). The base
.execute() validates params against input_schema and wraps exceptions.

Stdlib only (json / re / datetime) besides tools.tool_base + typing.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List

from tools.tool_base import Tool, ToolResult

# --------------------------------------------------------------------------
# helpers (pure, deterministic)
# --------------------------------------------------------------------------

# Laravel column-type map: everything unknown collapses to string.
_MIGRATION_TYPE_MAP = {
    "string": "string",
    "int": "integer",
    "integer": "integer",
    "bool": "boolean",
    "boolean": "boolean",
    "text": "text",
}


def _snake(name: str) -> str:
    """Convert any identifier style to snake_case (UserProfile -> user_profile)."""
    s = re.sub(r"[\s\-]+", "_", (name or "").strip())
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", s)
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.lower().strip("_")


def _studly(name: str) -> str:
    """Convert any identifier style to StudlyCase (user_profile -> UserProfile)."""
    return "".join(p[:1].upper() + p[1:] for p in _snake(name).split("_") if p)


def _php_str(value: str) -> str:
    """Escape a value for a PHP single-quoted string literal."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def _utc_stamp() -> str:
    """Laravel migration timestamp: YYYY_MM_DD_HHMMSS (UTC)."""
    return datetime.now(timezone.utc).strftime("%Y_%m_%d_%H%M%S")


# --------------------------------------------------------------------------
# bkd.make_migration
# --------------------------------------------------------------------------
class MakeMigration(Tool):
    name = "bkd.make_migration"
    room = "BKD-05"
    summary = "Generate a Laravel migration PHP file and publish the schema to the SSoT."
    input_schema = {
        "type": "object",
        "required": ["table", "fields"],
        "properties": {
            "table": {"type": "string", "minLength": 1},
            "fields": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["name", "type"],
                    "properties": {
                        "name": {"type": "string", "minLength": 1},
                        "type": {"type": "string", "minLength": 1},
                        "nullable": {"type": "boolean"},
                    },
                },
            },
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        table = params["table"]
        fields = params["fields"]
        table_snake = _snake(table)
        if not table_snake:
            return ToolResult(ok=False, error="table name resolves to empty identifier")

        col_lines: List[str] = ["            $table->id();"]
        for field in fields:
            fname = field.get("name", "")
            fsnake = _snake(fname)
            if not fsnake:
                return ToolResult(ok=False, error="field name resolves to empty identifier: %r" % fname)
            method = _MIGRATION_TYPE_MAP.get(str(field.get("type", "")).lower(), "string")
            line = "            $table->%s('%s')" % (method, _php_str(fsnake))
            if field.get("nullable"):
                line += "->nullable()"
            line += ";"
            col_lines.append(line)
        col_lines.append("            $table->timestamps();")

        class_name = "Create%sTable" % _studly(table)
        php = (
            "<?php\n\n"
            "use Illuminate\\Database\\Migrations\\Migration;\n"
            "use Illuminate\\Database\\Schema\\Blueprint;\n"
            "use Illuminate\\Support\\Facades\\Schema;\n\n"
            "final class %s extends Migration\n" % class_name
            + "{\n"
            "    public function up(): void\n"
            "    {\n"
            "        Schema::create('%s', function (Blueprint $table) {\n" % _php_str(table_snake)
            + "\n".join(col_lines) + "\n"
            "        });\n"
            "    }\n\n"
            "    public function down(): void\n"
            "    {\n"
            "        Schema::dropIfExists('%s');\n" % _php_str(table_snake)
            + "    }\n"
            "}\n"
        )

        relpath = "migrations/%s_create_%s_table.php" % (_utc_stamp(), table_snake)
        abspath = self._write_artifact(relpath, php)

        # Publish the schema to the Single Source of Truth registry.
        registry = self.call_substrate(
            "registry", ["set-table", table_snake, "--fields", json.dumps(fields)]
        )

        return ToolResult(
            ok=True,
            output={
                "path": abspath,
                "table": table_snake,
                "columns": len(fields),
                "registry": registry,
            },
            artifacts=[abspath],
        )


# --------------------------------------------------------------------------
# bkd.make_api_resource
# --------------------------------------------------------------------------
class MakeApiResource(Tool):
    name = "bkd.make_api_resource"
    room = "BKD-05"
    summary = "Generate a Laravel API Resource class plus a thin controller stub."
    input_schema = {
        "type": "object",
        "required": ["name", "fields"],
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "fields": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string", "minLength": 1},
            },
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        base = _studly(params["name"])
        if not base:
            return ToolResult(ok=False, error="name resolves to empty identifier")
        fields = params["fields"]

        resource_class = "%sResource" % base
        controller_class = "%sController" % base

        array_lines: List[str] = []
        for f in fields:
            key = _snake(f)
            if not key:
                return ToolResult(ok=False, error="field resolves to empty identifier: %r" % f)
            array_lines.append("            '%s' => $this->%s," % (_php_str(key), key))

        resource_php = (
            "<?php\n\n"
            "namespace App\\Http\\Resources;\n\n"
            "use Illuminate\\Http\\Request;\n"
            "use Illuminate\\Http\\Resources\\Json\\JsonResource;\n\n"
            "final class %s extends JsonResource\n" % resource_class
            + "{\n"
            "    public function toArray(Request $request): array\n"
            "    {\n"
            "        return [\n"
            + "\n".join(array_lines) + "\n"
            "        ];\n"
            "    }\n"
            "}\n"
        )

        controller_php = (
            "<?php\n\n"
            "namespace App\\Http\\Controllers;\n\n"
            "use App\\Http\\Resources\\%s;\n" % resource_class
            + "use App\\Models\\%s;\n" % base
            + "use Illuminate\\Http\\Request;\n\n"
            "final class %s extends Controller\n" % controller_class
            + "{\n"
            "    public function index(Request $request)\n"
            "    {\n"
            "        return %s::collection(%s::all());\n" % (resource_class, base)
            + "    }\n\n"
            "    public function show(Request $request, int $id)\n"
            "    {\n"
            "        return new %s(%s::findOrFail($id));\n" % (resource_class, base)
            + "    }\n"
            "}\n"
        )

        resource_path = self._write_artifact(
            "app/Http/Resources/%s.php" % resource_class, resource_php
        )
        controller_path = self._write_artifact(
            "app/Http/Controllers/%s.php" % controller_class, controller_php
        )

        return ToolResult(
            ok=True,
            output={"resource_path": resource_path, "controller_path": controller_path},
            artifacts=[resource_path, controller_path],
        )


# --------------------------------------------------------------------------
# bkd.run_checks
# --------------------------------------------------------------------------
class RunChecks(Tool):
    name = "bkd.run_checks"
    room = "BKD-05"
    summary = "Run Laravel checks (pint/phpstan) via the check substrate; app may be absent."
    input_schema = {
        "type": "object",
        "properties": {"path": {"type": "string", "minLength": 1}},
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        args = ["laravel"]
        path = params.get("path")
        if path:
            args += ["--path", path]
        status = self.call_substrate("check", args)

        # Tool-level success: the substrate produced a recognizable status payload,
        # even when the app is unconfigured (checks report "unconfigured"). A true
        # transport failure (substrate missing) has no such payload -> ok=False.
        ran = isinstance(status, dict) and ("checks" in status or "stack" in status)
        if not ran:
            return ToolResult(ok=False, error=status.get("error", "check substrate failed"),
                              output=status)
        return ToolResult(ok=True, output=status)


TOOLS: List[type] = [MakeMigration, MakeApiResource, RunChecks]

SELFTEST_SAMPLES: Dict[str, Dict[str, Any]] = {
    "bkd.make_migration": {
        "table": "users",
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "email", "type": "string", "nullable": True},
            {"name": "age", "type": "integer"},
            {"name": "is_active", "type": "boolean"},
            {"name": "bio", "type": "text"},
        ],
    },
    "bkd.make_api_resource": {
        "name": "User",
        "fields": ["id", "name", "email"],
    },
    "bkd.run_checks": {},
}
