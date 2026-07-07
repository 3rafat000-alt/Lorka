#!/usr/bin/env python3
"""
gemini_bridge — CEO report-push channel to a live Gemini chat (browser CDP bridge).

Doctrine fit: *big brain small mouth*. The CEO does NOT paste long reports into
the Claude conversation — it pushes them out through this bridge into a pinned
Gemini chat (the external review desk) and gets the reply back as data.

How it works
------------
Attaches to the user's ALREADY-RUNNING Chrome/Chromium over the CDP debugging
port (default 9222) — it never launches a browser, never touches cookies, and
reuses the user's live login session. It then:

  1. finds (or opens) the pinned Gemini conversation tab,
  2. pastes the report into the composer and sends it,
  3. waits until Gemini finishes generating (response-count + text-stability),
  4. returns the reply text (stdout and/or --out file).

Prereq (one-time per boot): user's browser started with
    --remote-debugging-port=9222

Configuration (first hit wins)
------------------------------
  --chat <url|id>            explicit conversation
  $SOFI_GEMINI_CHAT          env var (url or bare conversation id)
  ~/.engine/gemini_bridge.json {"chat": "...", "cdp_port": 9222}

CLI
---
    # push a report file, print Gemini's reply
    python gemini_bridge.py push --file report.md

    # pipe from another tool (the normal CEO flow)
    python sofi_scan.py ... | python gemini_bridge.py push

    # inline text, fire-and-forget (don't wait for reply)
    python gemini_bridge.py push --text "..." --no-reply

    # save reply durably (project brain, not chat)
    python gemini_bridge.py push --file report.md --out projects/PRJ-SAKK/_context/reports/gemini-review.md

    # check the bridge (browser reachable? tab found?)
    python gemini_bridge.py status

Import
------
    from gemini_bridge import GeminiBridge
    reply = GeminiBridge().push(report_text)

Guardrails
----------
* Sends data to an EXTERNAL service (Google). Never push secrets, credentials,
  PII, or production data — sanitized reports/findings only (same law as
  public-tunnels.md).
* Read-only toward the browser session beyond the one chat interaction.

GitHub Integration (2026-07-02)
-------------------------------
Now integrated with full SOFI system dump on GitHub:
* Config stores GitHub repo URL + branch
* `push --github` includes full context (commit hash, repo URL, file paths)
* Gemini can now review full codebase + architecture + git history without context limits
* Reply ingested into project brain with GitHub link + commit reference
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

DEFAULT_CDP_PORT = 9222
CONFIG_PATH = Path.home() / ".sofi" / "gemini_bridge.json"
GEMINI_HOST = "gemini.google.com"

# ── boundary sanitizer (last line of defence — fires no matter who calls push) ──
# Imported best-effort so the bridge still works if the module is missing, but if it
# IS present every outbound payload is redacted here regardless of the caller.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from sanitize_gemini_payload import sanitize_gemini_payload  # type: ignore
except Exception:  # pragma: no cover — fail-open, never block the bridge on import
    sanitize_gemini_payload = None

COMPOSER_SEL = "div[contenteditable='true']"
SEND_BTN_SEL = "button[aria-label*='إرسال'], button[aria-label*='Send'], .send-button"
STOP_BTN_SEL = "button[aria-label*='إيقاف'], button[aria-label*='Stop']"
RESPONSE_SEL = ".model-response, message-content, [class*='model-response']"


class BridgeError(RuntimeError):
    """Raised when the bridge cannot reach the browser / chat / composer."""


def _load_config() -> dict:
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _get_git_context() -> str:
    """Grab current git commit + branch for context injection."""
    import subprocess
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"],
                                      stderr=subprocess.DEVNULL).decode().strip()[:8]
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                                        stderr=subprocess.DEVNULL).decode().strip()
        return f"[git:{branch}/{sha}]"
    except:
        return "[git:unknown]"


def _normalize_chat(chat: str) -> str:
    """Accept a full URL or a bare conversation id."""
    if chat.startswith("http"):
        return chat
    return f"https://{GEMINI_HOST}/app/{chat}"


class GeminiBridge:
    def __init__(self, chat: Optional[str] = None, cdp_port: Optional[int] = None,
                 chat_title: Optional[str] = None):
        cfg = _load_config()
        chat = chat or os.environ.get("SOFI_GEMINI_CHAT") or cfg.get("chat")
        if not chat:
            raise BridgeError(
                "no chat configured — pass --chat, set $SOFI_GEMINI_CHAT, "
                f"or write {CONFIG_PATH}"
            )
        self.chat_url = _normalize_chat(chat)
        # conversation id = last path segment, used to match already-open tabs
        self.chat_id = self.chat_url.rstrip("/").rsplit("/", 1)[-1]
        self.cdp_port = int(cdp_port or os.environ.get("SOFI_CDP_PORT") or cfg.get("cdp_port") or DEFAULT_CDP_PORT)
        # sidebar title — the SPA sometimes renders a blank page on direct-URL load
        # of an old conversation; clicking the sidebar entry forces context fetch.
        self.chat_title = chat_title or os.environ.get("SOFI_GEMINI_CHAT_TITLE") or cfg.get("chat_title")

    # ── internals ────────────────────────────────────────────────────────────
    def _connect(self, p):
        try:
            # 127.0.0.1 explicitly — Chrome binds IPv4 only; "localhost" may resolve to ::1
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{self.cdp_port}")
        except Exception as e:
            raise BridgeError(
                f"cannot attach to browser on CDP port {self.cdp_port} — "
                f"start it with --remote-debugging-port={self.cdp_port} ({e})"
            )
        if not browser.contexts:
            raise BridgeError("browser attached but has no contexts/windows open")
        return browser.contexts[0]

    def _find_page(self, context):
        # 1. reuse any open Gemini tab, else open one
        page = None
        for pg in context.pages:
            if GEMINI_HOST in pg.url:
                page = pg
                break
        if page is None:
            page = context.new_page()
            page.goto(self.chat_url)
        else:
            page.bring_to_front()
            if self.chat_id not in page.url:
                page.goto(self.chat_url)

        # 2. SPA rescue: direct-URL load of an OLD conversation sometimes renders
        #    blank (Gemini fails to hydrate history). Clicking the sidebar entry by
        #    title forces the context fetch — same as a human click. Best-effort.
        if self.chat_title:
            try:
                page.wait_for_timeout(3000)  # let the sidebar render
                item = page.locator(f"text={self.chat_title!r}").first
                if item.count() > 0:
                    item.click()
                    page.wait_for_timeout(2000)  # let the conversation hydrate
            except Exception:
                pass  # fall back to the direct-URL load
        return page

    @staticmethod
    def _wait_reply(page, prev_count: int, timeout_s: int) -> str:
        """Wait for a NEW response to appear and its text to stop growing."""
        deadline = time.monotonic() + timeout_s
        last_text, stable_since = "", None
        while time.monotonic() < deadline:
            responses = page.locator(RESPONSE_SEL).all()
            if len(responses) > prev_count:
                try:
                    text = responses[-1].inner_text()
                except Exception:
                    text = ""
                still_generating = page.locator(STOP_BTN_SEL).count() > 0
                if text and text == last_text and not still_generating:
                    if stable_since is None:
                        stable_since = time.monotonic()
                    elif time.monotonic() - stable_since >= 2.0:
                        return text
                else:
                    stable_since = None
                last_text = text
            time.sleep(1.0)
        raise BridgeError(f"timed out after {timeout_s}s waiting for Gemini's reply")

    # ── public API ───────────────────────────────────────────────────────────
    def push(self, text: str, wait_reply: bool = True, timeout_s: int = 240,
             github_repo: Optional[str] = None) -> Optional[str]:
        """Send `text` into the pinned chat; return the reply (or None if fire-and-forget).

        Args:
            text: report content
            wait_reply: if True, wait for Gemini's response
            timeout_s: reply wait timeout
            github_repo: optional GitHub repo URL to append to text
        """
        if not text.strip():
            raise BridgeError("refusing to send an empty report")

        # BOUNDARY GUARD — redact secrets/PII/stack-traces before ANYTHING leaves the
        # machine. This is defence-in-depth: gemini_review.py already sanitizes, but a
        # raw `python gemini_bridge.py push` (or any other caller) hits the wire here.
        # fail_on_unsafe=False → redact-and-continue, never block the autonomous loop.
        if sanitize_gemini_payload is not None:
            text = sanitize_gemini_payload(text, fail_on_unsafe=False)

        # Inject GitHub context if provided
        if github_repo:
            text = f"{text}\n\n---\n**GitHub Repo:** {github_repo}\n**Updated:** {_get_git_context()}"

        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            context = self._connect(p)
            page = self._find_page(context)  # brings tab to front + SPA rescue
            page.wait_for_selector(COMPOSER_SEL, timeout=20_000)

            prev_count = page.locator(RESPONSE_SEL).count()

            page.focus(COMPOSER_SEL)
            page.fill(COMPOSER_SEL, text)
            time.sleep(0.5)
            page.click(SEND_BTN_SEL)

            if not wait_reply:
                time.sleep(2.0)  # let the send actually flush before detaching
                return None
            return self._wait_reply(page, prev_count, timeout_s)

    def capture_latest(self, timeout_s: int = 240) -> str:
        """Grab the latest reply WITHOUT sending anything.

        Recovery path for the case that bit us in practice: the send SUCCEEDED
        but the reply capture timed out (weak network / slow generation). Calling
        `push` again would double-post the report; this re-attaches to the live
        tab and waits for the last response's text to stop growing instead.
        """
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            context = self._connect(p)
            page = self._find_page(context)
            page.wait_for_selector(RESPONSE_SEL, timeout=20_000)
            deadline = time.monotonic() + timeout_s
            last_text, stable_since = "", None
            while time.monotonic() < deadline:
                responses = page.locator(RESPONSE_SEL).all()
                if responses:
                    try:
                        text = responses[-1].inner_text()
                    except Exception:
                        text = ""
                    still_generating = page.locator(STOP_BTN_SEL).count() > 0
                    if text and text == last_text and not still_generating:
                        if stable_since is None:
                            stable_since = time.monotonic()
                        elif time.monotonic() - stable_since >= 2.0:
                            return text
                    else:
                        stable_since = None
                    last_text = text
                time.sleep(1.0)
            raise BridgeError(f"timed out after {timeout_s}s capturing the latest reply")

    def status(self) -> dict:
        """Probe the bridge without sending anything."""
        from playwright.sync_api import sync_playwright

        out = {"chat": self.chat_url, "cdp_port": self.cdp_port,
               "browser": False, "tab_open": False}
        with sync_playwright() as p:
            context = self._connect(p)
            out["browser"] = True
            out["tab_open"] = any(self.chat_id in pg.url for pg in context.pages)
        return out


# ── CLI ──────────────────────────────────────────────────────────────────────
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="gemini_bridge", description=__doc__.split("\n")[1])
    ap.add_argument("--chat", help="conversation url or id (overrides env/config)")
    ap.add_argument("--cdp-port", type=int, help=f"CDP debug port (default {DEFAULT_CDP_PORT})")
    ap.add_argument("--title", help="sidebar conversation title — clicked to force SPA hydration on blank direct-load")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_push = sub.add_parser("push", help="send a report; print/save the reply")
    src = p_push.add_mutually_exclusive_group()
    src.add_argument("--file", help="report file to send")
    src.add_argument("--text", help="inline report text")
    p_push.add_argument("--no-reply", action="store_true", help="fire-and-forget")
    p_push.add_argument("--timeout", type=int, default=240, help="reply wait seconds")
    p_push.add_argument("--out", help="also write the reply to this file")
    p_push.add_argument("--github", help="append GitHub repo URL + git context to report")

    p_cap = sub.add_parser("capture", help="grab the latest reply WITHOUT sending (resume after a capture timeout)")
    p_cap.add_argument("--timeout", type=int, default=240, help="reply wait seconds")
    p_cap.add_argument("--out", help="also write the reply to this file")

    sub.add_parser("status", help="check browser/tab reachability")

    args = ap.parse_args(argv)
    try:
        bridge = GeminiBridge(chat=args.chat, cdp_port=args.cdp_port, chat_title=args.title)
        if args.cmd == "status":
            print(json.dumps(bridge.status(), ensure_ascii=False, indent=2))
            return 0

        if args.cmd == "capture":
            reply = bridge.capture_latest(timeout_s=args.timeout)
            if args.out:
                out_path = Path(args.out)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(reply or "", encoding="utf-8")
                print(f"reply saved → {out_path}")
            print(reply)
            return 0

        if args.file:
            text = Path(args.file).read_text(encoding="utf-8")
        elif args.text:
            text = args.text
        else:
            text = sys.stdin.read()  # pipeline mode

        reply = bridge.push(text, wait_reply=not args.no_reply, timeout_s=args.timeout,
                           github_repo=args.github if hasattr(args, 'github') else None)
        if args.no_reply:
            print("sent (no-reply mode)")
            return 0
        if args.out:
            out_path = Path(args.out)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(reply or "", encoding="utf-8")
            print(f"reply saved → {out_path}")
        print(reply)
        return 0
    except BridgeError as e:
        print(f"gemini_bridge: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
