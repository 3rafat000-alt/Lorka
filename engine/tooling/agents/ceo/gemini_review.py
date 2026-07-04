#!/usr/bin/env python3
"""
gemini_review — SOFI external-review desk (automated push → receive → parse → act).

This is the *plumbing* around `gemini_bridge`: the team no longer hand-drives a
raw push and eyeballs the reply. One call sends a report to the pinned Gemini
review desk, waits for the reply, and turns it into structured data the team acts
on — sanitized on the way out, ingested into the project brain on the way back.

Doctrine fit: *big brain small mouth* — the CEO/team spend zero conversation
tokens on long report/reply text; Python carries the payload both directions and
returns only the actionable distillate.

What it adds over the bare bridge (every item is a lesson learned in production)
--------------------------------------------------------------------------------
1. Sanitize-on-send   — redacts secrets/keys/passwords/.env values BEFORE the
                        report leaves the machine. External service = sanitized
                        only (same law as public-tunnels.md). Never blocks the
                        loop; it redacts and reports what it redacted.
2. Condense-if-long   — long report + weak network = capture timeout. Above a
                        char budget the report is condensed (drop code fences,
                        keep headings/bullets/the ask) so it sends fast.
3. Resilient capture  — if the SEND succeeded but the reply capture timed out,
                        the retry RE-CAPTURES (bridge.capture_latest) instead of
                        re-pushing, so the report is never double-posted.
4. Parse the reply    — split into sections + extract action items (severity /
                        SEV- / DELTA / imperative lines) as structured JSON.
5. Act on the brain   — save the reply under _context/reports/ and append an
                        auto-ingested digest to the project's HANDOFFS.md.

CLI
---
    # full loop: send a report, save + ingest the reply, print the distillate
    python gemini_review.py review --file report.md --prj PRJ-SAKK \\
        --out ~/Desktop/Lorka/projects/PRJ-SAKK/_context/reports/gemini-reply.md

    # append an explicit ask to the report before sending
    python gemini_review.py review --file report.md --prj PRJ-SAKK \\
        --ask "أجب بتقرير تصميم حل مفصّل واحترافي"

    # pipe a report in (the normal CEO flow)
    python sofi_scan.py ... | python gemini_review.py review --prj PRJ-SAKK

    # resume: the send went through last time but capture timed out
    python gemini_review.py capture --prj PRJ-SAKK --out .../gemini-reply.md

    # is the desk reachable?
    python gemini_review.py status

Import
------
    from gemini_review import ReviewDesk
    result = ReviewDesk().review(report_text, prj="PRJ-SAKK", out=path)
    for item in result["action_items"]:
        ...
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from gemini_bridge import GeminiBridge, BridgeError  # noqa: E402

# ── tunables ───────────────────────────────────────────────────────────────
CONDENSE_LIMIT = 6000       # chars; above this the report is condensed before send
DEFAULT_TIMEOUT = 300       # seconds to wait for a reply
MAX_RETRIES = 2             # extra attempts after the first
REDACTION = "«REDACTED»"

# Standing framing prepended to every push: the desk is NOT talking to a human — it
# is advising an autonomous AI agent (SOFI) that will EXECUTE the reply directly. This
# makes every reply come back as actionable, step-by-step, prioritized guidance.
AGENT_PREAMBLE = (
    "[سياق ثابت — اقرأه أولاً] أنت مستشار معماري كبير تُوجّه وكيلَ ذكاء اصطناعي ذاتي التشغيل "
    "(SOFI AI)، ولستَ تخاطب إنساناً. الوكيل سينفّذ توجيهك مباشرةً وبشكل مؤتمت بلا وسيط بشري. "
    "لذلك: أعطِ توجيهاً مفصّلاً ودقيقاً وقابلاً للتنفيذ خطوة بخطوة، لكل توصية سبب + أثر متوقّع + "
    "خطوة تنفيذ ملموسة، ومرتّباً بالأولوية. تجنّب العموميات؛ الوكيل يحتاج أوامر عمل لا نصائح عامة.\n\n"
)
DEFAULT_ASK = "أجب بتوجيه احترافي مفصّل قابل للتنفيذ فوراً، مرتّب بالأولوية، لكل بند سبب وأثر وخطوة تنفيذ."

# ── sanitizer: redact secrets before anything leaves the machine ────────────
# (value-group patterns redact only the sensitive tail, keeping the key/label so
#  the reviewer still sees the *shape* of the report.)
_SECRET_PATTERNS = [
    # PEM private keys — whole block
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"),
    # Stripe live/test secret + restricted keys
    re.compile(r"\b[sr]k_(?:live|test)_[0-9A-Za-z]{10,}\b"),
    # AWS access key id
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    # Google API key
    re.compile(r"\bAIza[0-9A-Za-z\-_]{30,}\b"),
    # Laravel APP_KEY / any base64: blob
    re.compile(r"base64:[A-Za-z0-9+/=]{20,}"),
    # Telegram bot token
    re.compile(r"\b\d{6,}:[A-Za-z0-9_-]{30,}\b"),
    # JWT
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
]
# key = value / key: value where the KEY names a secret
_ASSIGN_PATTERN = re.compile(
    r"(?i)\b([A-Z0-9_]*?(?:PASSWORD|PASSWD|SECRET|API[_-]?KEY|APP[_-]?SECRET|"
    r"ACCESS[_-]?KEY|PRIVATE[_-]?KEY|TOKEN|CLIENT[_-]?SECRET|DSN)[A-Z0-9_]*)"
    r"(\s*[:=]\s*)(['\"]?)([^\s'\"#]{4,})(\3)"
)


def sanitize(text: str) -> tuple[str, list[str]]:
    """Return (redacted_text, notes). Never raises; always redacts, never blocks."""
    notes: list[str] = []
    out = text
    for pat in _SECRET_PATTERNS:
        n = len(pat.findall(out))
        if n:
            out = pat.sub(REDACTION, out)
            notes.append(f"{n}× {pat.pattern[:28]}…")

    def _mask(m: re.Match) -> str:
        return f"{m.group(1)}{m.group(2)}{m.group(3)}{REDACTION}{m.group(5)}"

    n_assign = len(_ASSIGN_PATTERN.findall(out))
    if n_assign:
        out = _ASSIGN_PATTERN.sub(_mask, out)
        notes.append(f"{n_assign}× secret-assignment")
    return out, notes


# ── prune: remove duplicate errors + keep only state deltas (context preservation) ──
def prune(text: str) -> str:
    """Remove noisy repetition: duplicate stack traces, redundant error lines.
    Keep: headings, bullets, diffs, the ask, unique errors."""
    lines = text.splitlines()
    seen_errors: set[str] = set()
    out: list[str] = []
    skip_stack_until_blank = False

    for line in lines:
        s = line.strip()

        # Skip duplicate stack trace blocks
        if "File \"" in s or "line " in s and "in " in s:
            if skip_stack_until_blank:
                continue  # already logged this stack
            skip_stack_until_blank = True
        elif not s:
            skip_stack_until_blank = False

        # Skip duplicate error messages (keep only first occurrence)
        if s.startswith("Error:") or s.startswith("Exception:"):
            if s in seen_errors:
                continue
            seen_errors.add(s)

        # Keep: headings, bullets, diffs, questions, unique content
        if (re.match(r"^(#{1,6}\s|[-*]\s|\d+[.)]\s|>\s|\+|-|\-\-\-)", s)
                or "?" in s or "؟" in s
                or s.startswith("**") or s.endswith(":")
                or "@@ " in s):  # git diff markers
            out.append(line)
        elif s and len(s) > 10:
            out.append(line)

    return "\n".join(out).strip()


# ── condense: keep the signal, drop the bulk (weak-network safety) ──────────
def condense(text: str, limit: int = CONDENSE_LIMIT) -> str:
    if len(text) <= limit:
        return text
    t = re.sub(r"```[\s\S]*?```", "[code omitted]", text)     # drop fenced code
    t = re.sub(r"\n{3,}", "\n\n", t)                           # collapse blank runs
    if len(t) <= limit:
        return t
    keep: list[str] = []
    for line in t.splitlines():
        s = line.strip()
        if not s:
            continue
        if (re.match(r"^(#{1,6}\s|[-*]\s|\d+[.)]\s|>\s)", s)
                or s.startswith("**") or s.endswith(":")
                or "؟" in s or "?" in s):
            keep.append(line)
    cond = "\n".join(keep).strip()
    if len(cond) > limit:
        cond = cond[:limit].rstrip() + "\n… [condensed]"
    return cond


# ── parse the reply into structured, actionable data ───────────────────────
_HEADING = re.compile(r"^(#{1,6}\s+.+|\d+[.)]\s+.+|\*\*.+\*\*\s*$)")
_ACTION = re.compile(r"(حرج|عالي|متوسط|منخفض|🔴|🟠|🟡|SEV-|DELTA|Fail-(Open|Closed)|يجب|recommend|must)", re.I)


def parse_reply(reply: str) -> dict:
    sections: list[dict] = []
    cur = {"title": "(preamble)", "body": []}
    for line in reply.splitlines():
        s = line.strip()
        is_head = bool(_HEADING.match(s)) or (s.endswith(":") and 0 < len(s) < 80)
        if is_head:
            if cur["body"]:
                sections.append({"title": cur["title"], "body": "\n".join(cur["body"]).strip()})
            cur = {"title": s.lstrip("#*0123456789.) ").rstrip(":*").strip(), "body": []}
        else:
            cur["body"].append(line)
    if cur["body"]:
        sections.append({"title": cur["title"], "body": "\n".join(cur["body"]).strip()})

    seen, actions = set(), []
    for line in reply.splitlines():
        s = line.strip()
        if len(s) > 8 and _ACTION.search(s) and s not in seen:
            seen.add(s)
            actions.append(s)
    return {"sections": sections, "action_items": actions[:40], "length": len(reply)}


# ── brain integration ──────────────────────────────────────────────────────
def _sofi_paths():
    try:
        tooling = _HERE.parents[1]  # engine/tooling
        if str(tooling) not in sys.path:
            sys.path.insert(0, str(tooling))
        from sofi_tools import paths as _p  # type: ignore
        return _p
    except Exception:
        return None


def _brain_file(prj: str, stem: str) -> Optional[Path]:
    """Resolve a brain file by stem (e.g. "HANDOFFS"). sofi_tools.paths.brain_file
    adds the .md itself, so the fallback path adds it too — never double it."""
    p = _sofi_paths()
    if p:
        try:
            f = p.brain_file(prj, stem)
            if f:
                return f
        except Exception:
            pass
    base = Path(os.environ.get("SOFI_PROJECTS_DIR", str(Path.home() / "Desktop" / "projects")))
    f = base / prj / "_context" / f"{stem}.md"
    return f if f.parent.exists() else None


def _append_handoff(prj: str, result: dict) -> Optional[str]:
    hb = _brain_file(prj, "HANDOFFS")
    if not hb or not hb.exists():
        return None
    top = result["action_items"][:6]
    block = ["", "## EXTERNAL REVIEW (Gemini desk) — auto-ingested"]
    block.append(f"Reply saved: {result.get('saved') or '(not saved)'} · "
                 f"{len(result['sections'])} sections · {result['length']} chars"
                 + (f" · redacted {len(result['redactions'])} secret group(s) on send"
                    if result.get("redactions") else ""))
    if top:
        block.append("Top action items:")
        block += [f"- {a}" for a in top]
    hb.write_text(hb.read_text(encoding="utf-8") + "\n".join(block) + "\n", encoding="utf-8")
    return str(hb)


# ── orchestrator ───────────────────────────────────────────────────────────
class ReviewDesk:
    """Automated external-review desk over the Gemini bridge."""

    def __init__(self, chat: Optional[str] = None, cdp_port: Optional[int] = None,
                 chat_title: Optional[str] = None):
        self.bridge = GeminiBridge(chat=chat, cdp_port=cdp_port, chat_title=chat_title)

    def review(self, text: str, *, prj: Optional[str] = None, out: Optional[str] = None,
               ask: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT,
               do_condense: bool = True, do_sanitize: bool = True,
               retries: int = MAX_RETRIES, ingest: bool = True,
               preamble: bool = True) -> dict:
        if not text or not text.strip():
            raise BridgeError("refusing to send an empty report")
        # every push carries the standing "you advise an executing AI agent" framing
        if preamble:
            text = AGENT_PREAMBLE + text.rstrip()
        text = text.rstrip() + "\n\n---\n" + (ask.strip() if ask else DEFAULT_ASK) + "\n"

        redactions: list[str] = []
        if do_sanitize:
            text, redactions = sanitize(text)
        # Prune: remove duplicate errors + stack traces before sending (context preservation)
        text = prune(text)
        if do_condense:
            text = condense(text)

        reply, last_err, recapture = None, None, False
        for attempt in range(retries + 1):
            try:
                if recapture:
                    reply = self.bridge.capture_latest(timeout_s=timeout)
                else:
                    reply = self.bridge.push(text, wait_reply=True, timeout_s=timeout)
                if reply and reply.strip():
                    break
            except BridgeError as e:
                last_err = e
                # if the SEND went through and only the capture timed out, the next
                # attempt must RE-CAPTURE (never re-push — that double-posts).
                recapture = "timed out" in str(e).lower() and "captur" not in str(e).lower() \
                    or "reply" in str(e).lower()
                time.sleep(3 * (attempt + 1))
        if not reply or not reply.strip():
            raise BridgeError(f"review failed after {retries + 1} attempt(s): {last_err}")

        saved = None
        if out:
            sp = Path(out).expanduser()
            sp.parent.mkdir(parents=True, exist_ok=True)
            sp.write_text(reply, encoding="utf-8")
            saved = str(sp)

        result = {"reply": reply, "saved": saved, "redactions": redactions,
                  "sent_chars": len(text), **parse_reply(reply)}

        if ingest and prj:
            result["brain"] = _append_handoff(prj, result)
        return result

    def capture(self, *, prj: Optional[str] = None, out: Optional[str] = None,
                timeout: int = DEFAULT_TIMEOUT, ingest: bool = True) -> dict:
        reply = self.bridge.capture_latest(timeout_s=timeout)
        saved = None
        if out:
            sp = Path(out).expanduser()
            sp.parent.mkdir(parents=True, exist_ok=True)
            sp.write_text(reply, encoding="utf-8")
            saved = str(sp)
        result = {"reply": reply, "saved": saved, "redactions": [],
                  "sent_chars": 0, **parse_reply(reply)}
        if ingest and prj:
            result["brain"] = _append_handoff(prj, result)
        return result

    def status(self) -> dict:
        return self.bridge.status()


# ── CLI ────────────────────────────────────────────────────────────────────
def _print_result(result: dict, as_json: bool) -> None:
    if as_json:
        slim = {k: v for k, v in result.items() if k != "reply"}
        print(json.dumps(slim, ensure_ascii=False, indent=2))
        return
    if result.get("saved"):
        print(f"reply saved → {result['saved']}")
    if result.get("brain"):
        print(f"brain ingested → {result['brain']}")
    if result.get("redactions"):
        print(f"⚠ redacted before send: {', '.join(result['redactions'])}")
    items = result.get("action_items") or []
    if items:
        print(f"\n── {len(items)} action item(s) ──")
        for a in items[:20]:
            print(f"  • {a}")
    print(f"\n({len(result.get('sections', []))} sections · {result.get('length', 0)} chars)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="gemini_review",
                                 description="SOFI external-review desk (push→receive→parse→act)")
    ap.add_argument("--chat", help="conversation url or id (overrides env/config)")
    ap.add_argument("--cdp-port", type=int, help="CDP debug port")
    ap.add_argument("--title", help="sidebar conversation title (SPA hydration rescue)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("review", help="send a report; save + ingest + distill the reply")
    src = pr.add_mutually_exclusive_group()
    src.add_argument("--file", help="report file to send")
    src.add_argument("--text", help="inline report text")
    pr.add_argument("--prj", help="project id — ingest reply into its brain (HANDOFFS.md)")
    pr.add_argument("--out", help="write the reply to this file")
    pr.add_argument("--ask", help="explicit ask appended to the report before sending")
    pr.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="reply wait seconds")
    pr.add_argument("--no-condense", action="store_true", help="send the report verbatim")
    pr.add_argument("--no-sanitize", action="store_true", help="do NOT redact secrets (unsafe)")
    pr.add_argument("--no-ingest", action="store_true", help="do not append to the brain")
    pr.add_argument("--no-preamble", action="store_true", help="omit the standing 'you advise an executing AI agent' framing")
    pr.add_argument("--json", action="store_true", help="machine-readable output")

    pc = sub.add_parser("capture", help="grab the latest reply WITHOUT sending (resume path)")
    pc.add_argument("--prj", help="project id — ingest reply into its brain")
    pc.add_argument("--out", help="write the reply to this file")
    pc.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    pc.add_argument("--no-ingest", action="store_true")
    pc.add_argument("--json", action="store_true")

    sub.add_parser("status", help="check desk reachability")

    args = ap.parse_args(argv)
    try:
        desk = ReviewDesk(chat=args.chat, cdp_port=args.cdp_port, chat_title=args.title)

        if args.cmd == "status":
            print(json.dumps(desk.status(), ensure_ascii=False, indent=2))
            return 0

        if args.cmd == "capture":
            result = desk.capture(prj=args.prj, out=args.out, timeout=args.timeout,
                                  ingest=not args.no_ingest)
            _print_result(result, args.json)
            return 0

        # review
        if args.file:
            text = Path(args.file).expanduser().read_text(encoding="utf-8")
        elif args.text:
            text = args.text
        else:
            text = sys.stdin.read()
        result = desk.review(text, prj=args.prj, out=args.out, ask=args.ask,
                             timeout=args.timeout, do_condense=not args.no_condense,
                             do_sanitize=not args.no_sanitize, ingest=not args.no_ingest,
                             preamble=not args.no_preamble)
        _print_result(result, args.json)
        return 0
    except BridgeError as e:
        print(f"gemini_review: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
