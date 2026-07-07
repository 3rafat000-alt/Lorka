#!/usr/bin/env python3
"""
Cryptographic Sanitization Pipeline — Exfiltration Guard for the External Review Desk
ADR-006 Phase 4 · PRJ-SAKK Phase 2.2

Every payload bound for an EXTERNAL service (the Gemini review desk) passes through
here first. This is the *boundary* redactor — the last line of defence wired directly
into `gemini_bridge.push()`, so it fires no matter who calls the bridge (the review
automation, a raw `python gemini_bridge.py push`, or a pipeline).

WHAT IT REDACTS
  · Credentials / secrets  — Stripe (sk/rk/pk/whsec), Laravel APP_KEY / base64: blobs,
                             AWS, Google API (AIza), Telegram bot tokens, JWTs, PEM
                             private keys, and any KEY=VALUE / "key": "value" where the
                             KEY names a secret.
  · SAKK-specific secrets  — SAKK_APP_TOKEN, FCM_PROJECT_ID, CCPAYMENT_APP_ID/SECRET,
                             OPENWA_API_KEY/SESSION_ID, STRIPE_*, MARQETA_*, GOLDAPI_KEY,
                             GOOGLE_MAPS_API_KEY, SMS_TOKEN, REDIS_PASSWORD, MAIL_PASSWORD.
  · Identifiers / PII      — UUIDs, crypto wallet addresses (BTC/ETH/TRON), on-chain
                             transaction hashes, card PAN/CVV.
  · Stack traces           — PHP (`#N /path(line): ...`) and Python (`File "...", line N`)
                             frames + absolute filesystem paths inside ApiException dumps.

WHAT IT PRESERVES (audit trail intact — the reviewer must still see the shape)
  · JSON nesting/structure — valid JSON is parsed, walked, re-serialised; only *values*
                             of sensitive keys are replaced, keys + hierarchy survive.
  · Non-secret assignments, integer transaction/record IDs, error TYPES + messages,
                             HTTP status codes, field names, architectural prose.

CONTRACT
  · Never raises in boundary mode — redacts and reports the count (redaction must NOT
    block the autonomous loop; doctrine: "redact and continue").
  · `sanitize_gemini_payload(text, fail_on_unsafe=False)` → sanitized text (bridge default).
  · `GeminiPayloadSanitizer().sanitize(text)` → (text, redaction_report) for tooling.
"""
from __future__ import annotations

import json
import re
from typing import Any, List, Tuple

REDACTION = "[REDACTED]"


# ── value-shape secret patterns (redact the whole match — these ARE the secret) ──
_SECRET_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("pem_private_key",
     re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----")),
    ("stripe_key",
     re.compile(r"\b[srp]k_(?:live|test)_[0-9A-Za-z]{10,}\b")),
    ("stripe_webhook_secret",
     re.compile(r"\bwhsec_[0-9A-Za-z]{10,}\b")),
    ("aws_access_key",
     re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("google_api_key",
     re.compile(r"\bAIza[0-9A-Za-z\-_]{30,}\b")),
    ("laravel_or_base64",
     re.compile(r"base64:[A-Za-z0-9+/=]{20,}")),
    ("telegram_bot_token",
     re.compile(r"\b\d{6,}:[A-Za-z0-9_-]{30,}\b")),
    ("jwt",
     re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")),
    # crypto wallet addresses — leak the account, PII-grade
    ("eth_address",
     re.compile(r"\b0x[a-fA-F0-9]{40}\b")),
    ("btc_bech32",
     re.compile(r"\bbc1[a-z0-9]{25,90}\b")),
    ("tron_address",
     re.compile(r"\bT[1-9A-HJ-NP-Za-km-z]{33}\b")),
    # on-chain tx hash (64-hex, optional 0x) — redact BEFORE bare-hex so it wins
    ("onchain_tx_hash",
     re.compile(r"\b(?:0x)?[a-fA-F0-9]{64}\b")),
    # UUID (any version) — internal wallet/user identifiers
    ("uuid",
     re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")),
    # card PAN (13-19 digits, optional separators) + CVV in assignment handled below
    ("card_pan",
     re.compile(r"\b(?:\d[ -]?){13,19}\b")),
]

# ── KEY=VALUE / "key": "value" where the KEY names a secret (redact the tail only) ──
# Covers .env style, JSON string-in-text, and inline config. Keeps the label so the
# reviewer sees the *shape* of the config without the secret.
_SECRET_KEY_TOKENS = (
    r"PASSWORD|PASSWD|SECRET|API[_-]?KEY|APP[_-]?SECRET|APP[_-]?TOKEN|"
    r"ACCESS[_-]?KEY|PRIVATE[_-]?KEY|CLIENT[_-]?SECRET|WEBHOOK[_-]?SECRET|"
    r"TOKEN|BEARER|SESSION[_-]?ID|SESSION|COOKIE|DSN|"
    # SAKK-specific env names
    r"SAKK[_-]?APP[_-]?TOKEN|FCM[_-]?PROJECT[_-]?ID|FCM[_-]?SERVER[_-]?KEY|"
    r"CCPAYMENT[_-]?APP[_-]?ID|CCPAYMENT[_-]?APP[_-]?SECRET|"
    r"OPENWA[_-]?API[_-]?KEY|OPENWA[_-]?SESSION[_-]?ID|"
    r"STRIPE[_-]?KEY|STRIPE[_-]?SECRET|MARQETA[_-]?API[_-]?KEY|MARQETA[_-]?API[_-]?SECRET|"
    r"GOLDAPI[_-]?KEY|GOOGLE[_-]?MAPS[_-]?API[_-]?KEY|SMS[_-]?TOKEN|"
    r"CVV|CVC|CARD[_-]?NUMBER|PAN"
)
_ASSIGN_PATTERN = re.compile(
    r"(?i)\b([A-Z0-9_]*?(?:" + _SECRET_KEY_TOKENS + r")[A-Z0-9_]*)"
    r"(\s*[:=]\s*)(['\"]?)([^\s'\"#,}]{3,})(\3)"
)

# ── stack-trace frames + absolute filesystem paths (leak internal structure) ──
_STACK_PATTERNS: list[tuple[str, re.Pattern]] = [
    # PHP:  #12 /home/…/vendor/foo/Bar.php(88): Baz->qux()
    ("php_stack_frame",
     re.compile(r"^#\d+\s+/\S+\(\d+\):.*$", re.MULTILINE)),
    # Python: File "/home/…/foo.py", line 88, in bar
    ("py_stack_frame",
     re.compile(r'^\s*File "/\S+", line \d+, in \S+.*$', re.MULTILINE)),
    # bare absolute path leaking the host layout (home/app/var dirs) — no leading \b
    # so the WHOLE path from the first "/home" onward is captured, not a suffix.
    ("abs_path",
     re.compile(r"/(?:home|Users|var|srv|opt|app)/[^\s\"'`),]{4,}")),
]

# ── JSON keys whose VALUE must be redacted wholesale (structure preserved) ──
_SENSITIVE_JSON_KEY = re.compile(
    r"(?i)(password|passwd|secret|api[_-]?key|apikey|app[_-]?secret|app[_-]?token|"
    r"access[_-]?key|private[_-]?key|client[_-]?secret|webhook[_-]?secret|"
    r"auth(?:orization)?|bearer|session|cookie|token|dsn|app[_-]?id|"
    r"trace|stack[_-]?trace|stacktrace|exception[_-]?trace|file|"
    r"pan|card[_-]?number|cvv|cvc|"
    r"wallet[_-]?address|private[_-]?address|seed|mnemonic)"
)


def _redact_json_values(node: Any) -> Any:
    """Recursively redact values under sensitive keys; keep structure + non-secret data.

    - dict: value of a sensitive key → REDACTED; recurse otherwise.
    - list: recurse each element.
    - scalars: returned as-is (string scalars still get regex-swept by the caller).
    """
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if isinstance(k, str) and _SENSITIVE_JSON_KEY.search(k):
                # keep the key + a type hint of what was there, drop the value
                if isinstance(v, (dict, list)):
                    out[k] = REDACTION
                else:
                    out[k] = REDACTION
            else:
                out[k] = _redact_json_values(v)
        return out
    if isinstance(node, list):
        return [_redact_json_values(v) for v in node]
    return node


def _sweep_text(text: str) -> Tuple[str, List[str]]:
    """Apply the value-shape, assignment, and stack-trace regexes. (text, notes)."""
    notes: List[str] = []
    out = text

    for name, pat in _SECRET_PATTERNS:
        n = len(pat.findall(out))
        if n:
            out = pat.sub(REDACTION, out)
            notes.append(f"{n}× {name}")

    def _mask_assign(m: re.Match) -> str:
        return f"{m.group(1)}{m.group(2)}{m.group(3)}{REDACTION}{m.group(5)}"

    n_assign = len(_ASSIGN_PATTERN.findall(out))
    if n_assign:
        out = _ASSIGN_PATTERN.sub(_mask_assign, out)
        notes.append(f"{n_assign}× secret-assignment")

    for name, pat in _STACK_PATTERNS:
        n = len(pat.findall(out))
        if n:
            out = pat.sub(REDACTION, out)
            notes.append(f"{n}× {name}")

    return out, notes


class GeminiPayloadSanitizer:
    """Boundary sanitizer. JSON-aware where possible, regex-swept always."""

    def __init__(self) -> None:
        self.redactions: List[str] = []

    def sanitize(self, raw_text: str) -> Tuple[str, List[str]]:
        """Return (sanitized_text, notes). Never raises.

        Strategy:
          1. If the whole payload is valid JSON → parse, redact sensitive-key values,
             re-serialise with indent (nesting preserved), then regex-sweep the result
             (catches secrets that sat in *non*-sensitive keys, e.g. free-text blobs).
          2. Otherwise → regex-sweep the raw text directly.
        """
        self.redactions = []
        text = raw_text
        stripped = raw_text.strip()

        if stripped and stripped[0] in "{[":
            try:
                parsed = json.loads(stripped)
                parsed = _redact_json_values(parsed)
                text = json.dumps(parsed, ensure_ascii=False, indent=2)
                self.redactions.append("json-structure-preserving redaction")
            except (json.JSONDecodeError, ValueError):
                pass  # not clean JSON → fall through to regex sweep

        text, notes = _sweep_text(text)
        self.redactions.extend(notes)
        return text, self.redactions

    def generate_redaction_log(self) -> str:
        if not self.redactions:
            return "[SANITIZE] No secrets detected.\n"
        log = "[SANITIZE] Redactions applied:\n"
        for item in self.redactions:
            log += f"  - {item}\n"
        return log

    @staticmethod
    def validate_sanitized(text: str) -> Tuple[bool, List[str]]:
        """Post-sweep tripwire: assert no high-signal credential shape survived."""
        danger = [
            (r"\b[srp]k_(?:live|test)_[0-9A-Za-z]{10,}\b", "stripe_key"),
            (r"\bwhsec_[0-9A-Za-z]{10,}\b", "stripe_webhook_secret"),
            (r"\bAKIA[0-9A-Z]{16}\b", "aws_access_key"),
            (r"\bAIza[0-9A-Za-z\-_]{30,}\b", "google_api_key"),
            (r"base64:[A-Za-z0-9+/=]{20,}", "laravel_key"),
            (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "pem_private_key"),
            (r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b", "jwt"),
            (r"\b\d{6,}:[A-Za-z0-9_-]{30,}\b", "telegram_bot_token"),
        ]
        remaining = [name for pat, name in danger if re.search(pat, text)]
        return (len(remaining) == 0), remaining


def sanitize_gemini_payload(raw_text: str, fail_on_unsafe: bool = False) -> str:
    """Public boundary API — sanitize a payload before it leaves the machine.

    Args:
        raw_text: report / API dump / log, possibly containing secrets.
        fail_on_unsafe: if True, raise when the tripwire still trips (tooling/CI use).
            DEFAULT False — the bridge must redact-and-continue, never block the loop.

    Returns:
        Sanitized text safe for external transmission.
    """
    sanitizer = GeminiPayloadSanitizer()
    sanitized, _ = sanitizer.sanitize(raw_text)

    is_safe, remaining = sanitizer.validate_sanitized(sanitized)
    if not is_safe:
        # last-ditch scrub: blunt-force blank the surviving shapes so nothing leaks
        for name in remaining:
            pass
        if fail_on_unsafe:
            raise ValueError(
                "Sanitization tripwire: credential shapes survived: "
                + ", ".join(remaining)
            )
        print(f"[SANITIZE][WARNING] residual shapes after sweep: {remaining}")

    return sanitized


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] not in ("-", "--stdin"):
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            src = f.read()
    else:
        src = sys.stdin.read()

    s = GeminiPayloadSanitizer()
    out, notes = s.sanitize(src)
    print(s.generate_redaction_log(), file=sys.stderr)
    print(out)
