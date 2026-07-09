"""SEC-09 — Security room tools.

STRIDE threat modelling and a real (deterministic, read-only) secret scanner.
Artifacts land under .sofi/artifacts/SEC-09/. Stdlib + tools.tool_base + typing
only. No import-time side effects.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List

from tools.tool_base import ARTIFACTS_DIR, Tool, ToolResult

ROOM = "SEC-09"

_KEBAB_STRIP = re.compile(r"[^a-z0-9]+")
_KEBAB_DASH = re.compile(r"-+")


def kebab(text: str) -> str:
    """Lowercase, hyphenate, collapse — module-private slug helper."""
    s = _KEBAB_STRIP.sub("-", (text or "").strip().lower())
    s = _KEBAB_DASH.sub("-", s).strip("-")
    return s or "untitled"


# --------------------------------------------------------------------------- #
# STRIDE threat model                                                          #
# --------------------------------------------------------------------------- #
# category -> (generic threat, generic mitigation)
_STRIDE: List[tuple] = [
    ("Spoofing",
     "An attacker impersonates a legitimate identity to reach {asset}.",
     "Enforce strong authentication (MFA) and mutual TLS on access to {asset}."),
    ("Tampering",
     "Data in {asset} is modified in transit or at rest without authorization.",
     "Sign/checksum payloads, use TLS, and apply integrity constraints to {asset}."),
    ("Repudiation",
     "A user denies an action performed against {asset} with no reliable record.",
     "Emit append-only, timestamped audit logs for every mutation of {asset}."),
    ("Info-disclosure",
     "Sensitive contents of {asset} leak to an unauthorized party.",
     "Encrypt {asset} at rest and in transit; apply least-privilege access controls."),
    ("DoS",
     "{asset} is exhausted or made unavailable by flooding or resource abuse.",
     "Apply rate limiting, quotas, timeouts, and autoscaling around {asset}."),
    ("Elevation",
     "An attacker gains higher privileges than intended over {asset}.",
     "Deny by default, validate authorization on every request touching {asset}."),
]


class ThreatModel(Tool):
    name = "sec.threat_model"
    room = ROOM
    summary = "Generate a STRIDE threat-model markdown table seeded from the given assets."
    input_schema = {
        "type": "object",
        "required": ["feature", "assets"],
        "properties": {
            "feature": {"type": "string", "minLength": 1},
            "assets": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        feature = params["feature"]
        assets = [str(a) for a in params["assets"]]
        if not assets:
            return ToolResult(ok=False, error="assets must contain at least one entry")

        rows: List[str] = []
        for i, (category, threat_t, mit_t) in enumerate(_STRIDE):
            asset = assets[i % len(assets)]
            threat = threat_t.format(asset=asset)
            mitigation = mit_t.format(asset=asset)
            rows.append(f"| {category} | {threat} | `{asset}` | {mitigation} |")

        asset_list = ", ".join(f"`{a}`" for a in assets)
        md = "\n".join([
            f"# STRIDE Threat Model — {feature}",
            "",
            f"**Feature:** {feature}",
            f"**Assets ({len(assets)}):** {asset_list}",
            "",
            "## Threat Table",
            "",
            "| Category | Threat | Affected Asset | Mitigation |",
            "| --- | --- | --- | --- |",
            *rows,
            "",
            "## Notes",
            "",
            "- Each STRIDE category is seeded against an asset by round-robin; "
            "review and expand per real data flows.",
            "- Threats above are starting points, not an exhaustive analysis.",
            "",
        ])

        path = self._write_artifact(f"threat-models/{kebab(feature)}.md", md)
        return ToolResult(
            ok=True,
            output={"path": path, "feature": feature, "assets": len(assets)},
            artifacts=[path],
        )


# --------------------------------------------------------------------------- #
# Secret scanner                                                               #
# --------------------------------------------------------------------------- #
_EXCLUDE_DIRS = {".git", "node_modules", "vendor", "__pycache__"}
_EXCLUDE_FILES = {"tasks.db"}
_MAX_FILE_BYTES = 2_000_000  # skip anything larger — likely binary/build output

# (rule name, compiled pattern, value-group name or None -> use whole match)
_RULES: List[tuple] = [
    ("private_key",
     re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"), None),
    ("aws_access_key_id",
     re.compile(r"AKIA[0-9A-Z]{16}"), None),
    ("generic_secret_assignment",
     re.compile(r"(?i)(?:password|secret|api_key|token)\s*[:=]\s*['\"](?P<val>[^'\"]{6,})['\"]"),
     "val"),
]


def _mask(secret: str) -> str:
    """Reveal only the first and last two characters; never the middle."""
    if len(secret) <= 4:
        return "*" * len(secret)
    return f"{secret[:2]}{'*' * (len(secret) - 4)}{secret[-2:]}"


class SecretScan(Tool):
    name = "sec.secret_scan"
    room = ROOM
    summary = "Real read-only scan for leaked private keys, AWS key IDs, and secret assignments."
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "max_files": {"type": "integer"},
        },
    }

    def _iter_files(self, target: Path, max_files: int) -> List[Path]:
        if target.is_file():
            return [target]
        collected: List[Path] = []
        for root, dirs, files in os.walk(target):
            dirs[:] = sorted(d for d in dirs if d not in _EXCLUDE_DIRS)
            for fn in sorted(files):
                if len(collected) >= max_files:
                    return collected
                if fn in _EXCLUDE_FILES:
                    continue
                collected.append(Path(root) / fn)
        return collected

    def run(self, params: Dict[str, Any]) -> ToolResult:
        # SAFE default: the .sofi/artifacts dir — NEVER the whole repo.
        target = Path(params.get("path") or str(ARTIFACTS_DIR))
        max_files = params.get("max_files") or 500
        if max_files <= 0:
            max_files = 500

        if not target.exists():
            # Missing path is a valid (empty) report, not a failure.
            return ToolResult(
                ok=True,
                output={"scanned_files": 0, "findings": [], "count": 0},
            )

        findings: List[Dict[str, Any]] = []
        scanned = 0
        for fp in self._iter_files(target, max_files):
            try:
                if fp.stat().st_size > _MAX_FILE_BYTES:
                    continue
                text = fp.read_text(encoding="utf-8", errors="ignore")
            except (OSError, ValueError):
                continue
            scanned += 1
            for lineno, line in enumerate(text.splitlines(), 1):
                for rule, pattern, val_group in _RULES:
                    m = pattern.search(line)
                    if not m:
                        continue
                    secret = m.group(val_group) if val_group else m.group(0)
                    findings.append({
                        "file": str(fp),
                        "line": lineno,
                        "rule": rule,
                        "masked": _mask(secret),
                    })

        return ToolResult(
            ok=True,
            output={
                "scanned_files": scanned,
                "findings": findings,
                "count": len(findings),
            },
        )


TOOLS: List[type] = [ThreatModel, SecretScan]

SELFTEST_SAMPLES: Dict[str, Dict[str, Any]] = {
    "sec.threat_model": {
        "feature": "OAuth Login",
        "assets": ["session token", "user table", "OAuth client secret"],
    },
    # Empty params -> scans the SAFE default (.sofi/artifacts); ok even if empty.
    "sec.secret_scan": {},
}
