"""GTW-06 — API Gateway / Integration room tools.

Two capabilities:
  * gtw.route_spec        — emit a Kong-style declarative gateway config for a route.
  * gtw.validate_delegation — reuse the Maestro guard (substrate `validate`) to
                              grade an RCCF delegation payload.

Stdlib + tools.tool_base only. No import-time side effects.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from tools.tool_base import Tool, ToolResult


# --- module-private slug helpers -------------------------------------------
def _slug(text: str, sep: str) -> str:
    """Lowercase slug: split camelCase, collapse non-alnum runs to `sep`."""
    # break camelCase / PascalCase boundaries (fooBar -> foo Bar)
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text or "")
    parts = re.findall(r"[0-9A-Za-z]+", text)
    return sep.join(p.lower() for p in parts)


def kebab(text: str) -> str:
    return _slug(text, "-")


def snake(text: str) -> str:
    return _slug(text, "_")


def _norm_methods(methods: List[str]) -> List[str]:
    """Uppercase, de-duplicate (order-preserving) HTTP methods."""
    seen: List[str] = []
    for m in methods:
        u = str(m).strip().upper()
        if u and u not in seen:
            seen.append(u)
    return seen


# --- gtw.route_spec --------------------------------------------------------
class RouteSpecTool(Tool):
    name = "gtw.route_spec"
    room = "GTW-06"
    summary = "Generate a Kong-style declarative gateway config (service + route + plugins)."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["route", "upstream", "methods"],
        "properties": {
            "route": {"type": "string", "minLength": 1},
            "upstream": {"type": "string", "minLength": 1},
            "methods": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string", "minLength": 1},
            },
            "auth": {"type": "string", "enum": ["none", "jwt", "oauth2"]},
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        route = params["route"]
        upstream = params["upstream"]
        auth = params.get("auth", "none")
        methods = _norm_methods(params["methods"])
        if not methods:
            return ToolResult(ok=False, error="no valid HTTP methods supplied")

        base = kebab(route) or "root"

        # CORS mirrors the route's own verbs plus the preflight OPTIONS verb.
        cors_methods = list(methods)
        if "OPTIONS" not in cors_methods:
            cors_methods.append("OPTIONS")

        plugins: List[Dict[str, Any]] = [
            {
                "name": "rate-limiting",
                "config": {
                    "minute": 60,
                    "hour": 10000,
                    "policy": "local",
                    "fault_tolerant": True,
                    "hide_client_headers": False,
                },
            },
            {
                "name": "cors",
                "config": {
                    "origins": ["*"],
                    "methods": cors_methods,
                    "headers": ["Accept", "Authorization", "Content-Type"],
                    "exposed_headers": ["X-Request-Id"],
                    "credentials": False,
                    "max_age": 3600,
                    "preflight_continue": False,
                },
            },
        ]
        if auth == "jwt":
            plugins.append({
                "name": "jwt",
                "config": {
                    "claims_to_verify": ["exp"],
                    "key_claim_name": "iss",
                    "secret_is_base64": False,
                    "run_on_preflight": True,
                },
            })
        elif auth == "oauth2":
            plugins.append({
                "name": "oauth2",
                "config": {
                    "scopes": ["read", "write"],
                    "enable_authorization_code": True,
                    "enable_client_credentials": True,
                    "mandatory_scope": False,
                    "token_expiration": 7200,
                    "accept_http_if_already_terminated": False,
                },
            })

        config = {
            "_format_version": "3.0",
            "services": [
                {
                    "name": f"{base}-service",
                    "url": upstream,
                    "routes": [
                        {
                            "name": f"{base}-route",
                            "paths": [route],
                            "methods": methods,
                            "strip_path": False,
                            "preserve_host": True,
                        }
                    ],
                    "plugins": plugins,
                }
            ],
        }

        content = json.dumps(config, indent=2, ensure_ascii=False) + "\n"
        path = self._write_artifact(f"gateway/{base}.json", content)
        return ToolResult(
            ok=True,
            output={"path": path, "route": route, "methods": len(methods), "auth": auth},
            artifacts=[path],
        )


# --- gtw.validate_delegation -----------------------------------------------
class ValidateDelegationTool(Tool):
    name = "gtw.validate_delegation"
    room = "GTW-06"
    summary = "Grade an RCCF delegation payload via the Maestro guard (substrate validate)."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["payload"],
        "properties": {
            "payload": {"type": "object"},
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        payload = params["payload"]
        result = self.call_substrate(
            "validate", ["delegation", "--payload", json.dumps(payload)]
        )
        # A validator verdict always carries "schema" and/or "errors". Anything
        # else (missing substrate, non-JSON output) is an INTERNAL failure.
        if "schema" not in result and "errors" not in result:
            return ToolResult(
                ok=False,
                error=result.get("error") or "validator produced no verdict",
                output=result,
            )
        # Rejection of a bad payload is a CORRECT outcome -> tool-level ok=True;
        # the verdict (including any errors) lives in output.
        return ToolResult(ok=True, output=result)


TOOLS: List[type] = [RouteSpecTool, ValidateDelegationTool]

SELFTEST_SAMPLES: Dict[str, Dict[str, Any]] = {
    "gtw.route_spec": {
        "route": "/api/v1/orders",
        "upstream": "http://orders-svc:8080",
        "methods": ["GET", "POST"],
        "auth": "jwt",
    },
    "gtw.validate_delegation": {
        "payload": {
            "sender": "CEO_Agent",
            "recipient": "bck-api-engineer",
            "action": "CREATE_MIGRATION",
            "parameters": {"table": "users"},
            "context_priority": "HIGH",
        }
    },
}
