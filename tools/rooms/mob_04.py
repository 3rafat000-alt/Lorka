"""MOB-04 — Mobile (Flutter/Dart) room tools.

Deterministic code-generation capabilities the mobile room reaches for:
  * mob.model_from_contract — a Dart data class that matches the backend contract 100%.
  * mob.scaffold_widget     — a Flutter StatelessWidget (optionally a Form of fields).
  * mob.run_analyze         — reuse the `check` substrate to run `flutter analyze`.

Every tool subclasses tools.tool_base.Tool and implements only run(). The base
.execute() validates params against input_schema and wraps exceptions.

Stdlib only (re) besides tools.tool_base + typing.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

from tools.tool_base import Tool, ToolResult

# --------------------------------------------------------------------------
# helpers (pure, deterministic)
# --------------------------------------------------------------------------

# Dart type map: everything unknown collapses to dynamic (no silent guessing).
_DART_TYPE_MAP = {
    "string": "String",
    "int": "int",
    "integer": "int",
    "bool": "bool",
    "boolean": "bool",
    "double": "double",
    "float": "double",
}


def _snake(name: str) -> str:
    """Convert any identifier style to snake_case (UserProfile -> user_profile)."""
    s = re.sub(r"[\s\-]+", "_", (name or "").strip())
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", s)
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.lower().strip("_")


def _pascal(name: str) -> str:
    """Convert any identifier style to PascalCase (user_profile -> UserProfile)."""
    return "".join(p[:1].upper() + p[1:] for p in _snake(name).split("_") if p)


def _camel(name: str) -> str:
    """Convert any identifier style to camelCase (is_active -> isActive)."""
    p = _pascal(name)
    return p[:1].lower() + p[1:] if p else p


def _dart_str(value: str) -> str:
    """Escape a value for a Dart single-quoted string literal."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


# --------------------------------------------------------------------------
# mob.model_from_contract
# --------------------------------------------------------------------------
class ModelFromContract(Tool):
    name = "mob.model_from_contract"
    room = "MOB-04"
    summary = "Generate a Dart data class (fromJson/toJson) matching the backend contract."
    input_schema = {
        "type": "object",
        "required": ["model", "fields"],
        "properties": {
            "model": {"type": "string", "minLength": 1},
            "fields": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["name", "type"],
                    "properties": {
                        "name": {"type": "string", "minLength": 1},
                        "type": {"type": "string", "minLength": 1},
                    },
                },
            },
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        class_name = _pascal(params["model"])
        if not class_name:
            return ToolResult(ok=False, error="model resolves to empty identifier")
        fields = params["fields"]

        resolved: List[Dict[str, str]] = []
        for f in fields:
            ident = _camel(f.get("name", ""))
            if not ident:
                return ToolResult(ok=False, error="field name resolves to empty identifier: %r"
                                  % f.get("name"))
            dart_type = _DART_TYPE_MAP.get(str(f.get("type", "")).lower(), "dynamic")
            json_key = f.get("name", "")
            resolved.append({"ident": ident, "type": dart_type, "key": json_key})

        field_decls = "\n".join(
            "  final %s %s;" % (r["type"], r["ident"]) for r in resolved
        )
        ctor_params = "\n".join(
            "    required this.%s," % r["ident"] for r in resolved
        )

        from_lines: List[str] = []
        for r in resolved:
            access = "json['%s']" % _dart_str(r["key"])
            if r["type"] == "dynamic":
                from_lines.append("      %s: %s," % (r["ident"], access))
            else:
                from_lines.append("      %s: %s as %s," % (r["ident"], access, r["type"]))
        from_body = "\n".join(from_lines)

        to_body = "\n".join(
            "      '%s': %s," % (_dart_str(r["key"]), r["ident"]) for r in resolved
        )

        dart = (
            "class %s {\n" % class_name
            + field_decls + "\n\n"
            "  const %s({\n" % class_name
            + ctor_params + "\n"
            "  });\n\n"
            "  factory %s.fromJson(Map<String, dynamic> json) {\n" % class_name
            + "    return %s(\n" % class_name
            + from_body + "\n"
            "    );\n"
            "  }\n\n"
            "  Map<String, dynamic> toJson() {\n"
            "    return {\n"
            + to_body + "\n"
            "    };\n"
            "  }\n"
            "}\n"
        )

        relpath = "models/%s.dart" % _snake(params["model"])
        abspath = self._write_artifact(relpath, dart)

        return ToolResult(
            ok=True,
            output={"path": abspath, "model": class_name, "fields": len(fields)},
            artifacts=[abspath],
        )


# --------------------------------------------------------------------------
# mob.scaffold_widget
# --------------------------------------------------------------------------
class ScaffoldWidget(Tool):
    name = "mob.scaffold_widget"
    room = "MOB-04"
    summary = "Generate a Flutter StatelessWidget; a Form of TextFormFields when fields given."
    input_schema = {
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "fields": {"type": "array", "items": {"type": "string", "minLength": 1}},
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        class_name = _pascal(params["name"])
        if not class_name:
            return ToolResult(ok=False, error="name resolves to empty identifier")
        fields = params.get("fields") or []

        if fields:
            field_widgets = "\n".join(
                "          TextFormField(\n"
                "            decoration: const InputDecoration(labelText: '%s'),\n"
                "          )," % _dart_str(f)
                for f in fields
            )
            body = (
                "    return Form(\n"
                "      child: Column(\n"
                "        mainAxisSize: MainAxisSize.min,\n"
                "        children: [\n"
                + field_widgets + "\n"
                "        ],\n"
                "      ),\n"
                "    );\n"
            )
        else:
            body = (
                "    return const Center(\n"
                "      child: Text('%s'),\n" % _dart_str(class_name)
                + "    );\n"
            )

        dart = (
            "import 'package:flutter/material.dart';\n\n"
            "class %s extends StatelessWidget {\n" % class_name
            + "  const %s({super.key});\n\n" % class_name
            + "  @override\n"
            "  Widget build(BuildContext context) {\n"
            + body
            + "  }\n"
            "}\n"
        )

        relpath = "widgets/%s.dart" % _snake(params["name"])
        abspath = self._write_artifact(relpath, dart)

        return ToolResult(
            ok=True,
            output={"path": abspath, "name": class_name},
            artifacts=[abspath],
        )


# --------------------------------------------------------------------------
# mob.run_analyze
# --------------------------------------------------------------------------
class RunAnalyze(Tool):
    name = "mob.run_analyze"
    room = "MOB-04"
    summary = "Run `flutter analyze`/`flutter test` via the check substrate; app may be absent."
    input_schema = {
        "type": "object",
        "properties": {"path": {"type": "string", "minLength": 1}},
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        args = ["flutter"]
        path = params.get("path")
        if path:
            args += ["--path", path]
        status = self.call_substrate("check", args)

        # Tool-level success: the substrate produced a recognizable status payload,
        # even when the app is unconfigured. A true transport failure (substrate
        # missing) carries no such payload -> ok=False.
        ran = isinstance(status, dict) and ("checks" in status or "stack" in status)
        if not ran:
            return ToolResult(ok=False, error=status.get("error", "check substrate failed"),
                              output=status)
        return ToolResult(ok=True, output=status)


TOOLS: List[type] = [ModelFromContract, ScaffoldWidget, RunAnalyze]

SELFTEST_SAMPLES: Dict[str, Dict[str, Any]] = {
    "mob.model_from_contract": {
        "model": "UserProfile",
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "age", "type": "integer"},
            {"name": "is_active", "type": "boolean"},
            {"name": "score", "type": "double"},
            {"name": "meta", "type": "json"},
        ],
    },
    "mob.scaffold_widget": {
        "name": "ProfileForm",
        "fields": ["name", "email"],
    },
    "mob.run_analyze": {},
}
