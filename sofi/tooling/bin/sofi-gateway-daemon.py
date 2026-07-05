#!/usr/bin/env python3
"""SOFI Gateway Daemon v2 — n8n <-> Claude Code bridge (host-side).

Listens on 127.0.0.1:8099. n8n workflows POST work here; the daemon builds an
RCCF block, runs `claude -p` on the host (full CLI/git/brain access), and either
answers inline (sync) or queues the job and POSTs the result to a callback
webhook when done (async — the WhatsApp path).

Endpoints
  GET  /healthz            liveness (no auth)
  POST /dispatch           auth; {command, role?, project?, model?, mode?,
                           callback_url?, timeout?, context?, source?, meta?}
                           mode=sync  -> blocks, returns result (quick ops)
                           mode=async -> returns {job_id} instantly (default)
  GET  /job/<id>           auth; job status + result
  GET  /jobs               auth; recent jobs (bounded)

Security
  - binds 127.0.0.1 only; token via X-SOFI-Token (constant-time compare)
  - role allowlist = .claude/agents/*.md (name-validated, no path escape)
  - model allowlist fixed; callback_url host allowlist (SOFI_CALLBACK_ALLOW)
  - optional owner-chat gate for whatsapp sources (SOFI_OWNER_CHAT)
  - body cap 256 KiB; global rate limit; sync concurrency cap
  - every job persisted to ~/.sofi-run/gateway-jobs.jsonl (rotated audit trail);
    lost callbacks land in ~/.sofi-run/gateway-callback-deadletter.jsonl

Owner: devops-cloud-lead. Gate: tool-plane (not a project).
"""
from __future__ import annotations

import hmac
import json
import logging
import logging.handlers
import os
import queue
import re
import signal
import subprocess
import threading
import time
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WORKSPACE = Path(os.environ.get("SOFI_WORKSPACE", "/home/es3dlll/Desktop/Lorka"))
BIND = os.environ.get("SOFI_GATEWAY_BIND", "127.0.0.1")
PORT = int(os.environ.get("SOFI_GATEWAY_PORT", "8099"))
TOKEN = os.environ.get("SOFI_GATEWAY_TOKEN", "")
CLAUDE_BIN = os.environ.get("SOFI_CLAUDE_BIN", str(Path.home() / ".local/bin/claude"))

SYNC_TIMEOUT = 180          # sync jobs must be quick
ASYNC_TIMEOUT_DEFAULT = 1800
ASYNC_TIMEOUT_MAX = 3600
MAX_BODY = 256 * 1024
MAX_WORKERS = 2             # concurrent claude runs
RATE_LIMIT_PER_MIN = 20     # global dispatch cap — runaway-loop protection
JOBS_KEEP = 200             # in-memory job records
SYNC_SLOTS = int(os.environ.get("SOFI_SYNC_SLOTS", "3"))  # concurrent sync claude runs
RESULT_CAP = 4000           # max chars of `result` written to the jsonl audit line
JSONL_MAX = 10 * 1024 * 1024  # rotate gateway-jobs.jsonl past this size

MODEL_ALLOW = {"haiku", "sonnet", "opus", "claude-fable-5", "fable"}
MODEL_DEFAULT = "haiku"

# callback SSRF/token-leak guard: only POST the X-SOFI-Token to known hosts
CALLBACK_ALLOW = {h.strip() for h in os.environ.get(
    "SOFI_CALLBACK_ALLOW", "127.0.0.1:5678,localhost:5678").split(",") if h.strip()}
# defense-in-depth sender gate for whatsapp sources (empty = disabled, n8n gates)
OWNER_CHAT = os.environ.get("SOFI_OWNER_CHAT", "")

RUN_DIR = Path.home() / ".sofi-run"
LOG_DIR = RUN_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
JOBS_FILE = RUN_DIR / "gateway-jobs.jsonl"
DEADLETTER_FILE = RUN_DIR / "gateway-callback-deadletter.jsonl"

_log_handler = logging.handlers.RotatingFileHandler(
    str(LOG_DIR / "sofi-gateway.log"), maxBytes=10 * 1024 * 1024, backupCount=5,
    encoding="utf-8")
_log_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[_log_handler])
log = logging.getLogger("sofi-gateway")


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def coerce_timeout(value, default: int, cap: int) -> int:
    """Bound a caller-supplied timeout to a positive int <= cap; default on junk
    (None, "5m", floats-as-str, <=0). Used by both sync and async paths."""
    try:
        t = int(value)
    except (TypeError, ValueError):
        return default
    if t <= 0:
        return default
    return min(t, cap)


def timeout_coercible(value) -> bool:
    """True iff `value` is a positive-int timeout (dispatch-time 400 guard)."""
    try:
        return int(value) > 0
    except (TypeError, ValueError):
        return False


# ───────────────────────── agents / RCCF ─────────────────────────

def resolve_agent(role: str) -> str | None:
    """Return the canonical agent name if the spec exists, else None.
    `role` is name-validated then path-confined so `../../MEMORY` can't escape."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", role or ""):
        return None  # reject traversal/junk before touching the filesystem
    agents = (WORKSPACE / ".claude" / "agents").resolve()
    for cand in (f"{role}.md", f"sofi-{role}.md"):
        path = (agents / cand).resolve()
        if not str(path).startswith(str(agents) + os.sep):
            continue  # candidate escaped the agents dir — refuse
        if path.is_file():
            return cand[:-3]
    return None


def head_sha(project: str) -> str:
    state = WORKSPACE / "projects" / project / "_context" / "STATE.md"
    if state.is_file():
        try:
            for line in state.read_text(encoding="utf-8", errors="ignore").splitlines():
                if line.startswith("head_sha:"):
                    return line.split(":", 1)[1].strip().split()[0]
        except OSError:
            pass
    return "unknown"


def build_prompt(p: dict, role: str) -> str:
    project = p.get("project", "PRJ-SAKK")
    parts = [
        f"🎭 **Role:** {role}",
        "📂 **Context:**",
        f"- Project: {project}",
        f"- HEAD: {head_sha(project)}",
        f"- Priority: {p.get('priority', 'medium')}",
        f"- Source: {p.get('source', 'n8n')}",
    ]
    if p.get("context"):
        parts.append(f"- Extra: {p['context']}")
    parts += [
        "",
        f"🎯 **Command:**\n{p['command']}",
        "",
        "📐 **Format:**\n"
        + p.get("format",
                "Do the work per SOFI doctrine (sync -> act -> checkpoint -> handoff). "
                "Finish with a short Arabic summary (<= 900 chars) of what was done, "
                "suitable to send as a WhatsApp message."),
    ]
    return "\n".join(parts)


# ───────────────────────── job store ─────────────────────────

class Jobs:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jobs: dict[str, dict] = {}
        self._order: list[str] = []

    def create(self, payload: dict, mode: str) -> dict:
        jid = uuid.uuid4().hex[:12]
        job = {
            "job_id": jid, "status": "queued", "mode": mode,
            # resolved role (payload["_role"]) preferred over the raw request role
            "role": payload.get("_role") or payload.get("role"),
            "project": payload.get("project", "PRJ-SAKK"),
            "command": payload.get("command", "")[:500],
            "source": payload.get("source", "n8n"),
            "meta": payload.get("meta"), "created": now_iso(),
            "started": None, "finished": None, "result": None, "error": None,
            "callback_status": None,
        }
        with self._lock:
            self._jobs[jid] = job
            self._order.append(jid)
            while len(self._order) > JOBS_KEEP:
                self._jobs.pop(self._order.pop(0), None)
        return dict(job)

    def get(self, jid: str) -> dict | None:
        with self._lock:
            job = self._jobs.get(jid)
            return dict(job) if job else None  # copy — avoid torn reads

    def update(self, jid: str, **kv) -> None:
        with self._lock:
            if jid in self._jobs:
                self._jobs[jid].update(kv)

    def recent(self, limit: int = 20) -> list[dict]:
        with self._lock:
            return [dict(self._jobs[j]) for j in self._order[-limit:]][::-1]  # copies


JOBS = Jobs()
WORK_Q: "queue.Queue[tuple[dict, dict]]" = queue.Queue(maxsize=50)
SYNC_SEM = threading.Semaphore(SYNC_SLOTS)  # caps concurrent in-thread sync claude runs


def _rotate_jobs_file() -> None:
    """Keep gateway-jobs.jsonl bounded: rename to .1 (one backup) past JSONL_MAX."""
    try:
        if JOBS_FILE.exists() and JOBS_FILE.stat().st_size > JSONL_MAX:
            JOBS_FILE.replace(JOBS_FILE.parent / (JOBS_FILE.name + ".1"))
    except OSError as e:
        log.error("jobs rotate failed: %s", e)


def persist(job: dict) -> None:
    _rotate_jobs_file()
    rec = dict(job)
    r = rec.get("result")
    if isinstance(r, str) and len(r) > RESULT_CAP:
        rec["result"] = r[:RESULT_CAP]  # cap audit line; full result stays in-memory/callback
    try:
        with open(JOBS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError as e:
        log.error("persist failed: %s", e)


def deadletter(body: dict) -> None:
    """Capture an undeliverable callback so a reply is never silently lost."""
    try:
        with open(DEADLETTER_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(body, ensure_ascii=False) + "\n")
    except OSError as e:
        log.error("deadletter write failed: %s", e)


# ───────────────────────── claude execution ─────────────────────────

def run_claude(payload: dict, role: str, timeout: int) -> dict:
    prompt = build_prompt(payload, role)
    model = payload.get("model", MODEL_DEFAULT)
    cmd = [
        CLAUDE_BIN, "-p", prompt,
        "--model", model,
        "--output-format", "json",
        "--dangerously-skip-permissions",
    ]
    log.info("run role=%s model=%s timeout=%s cmd_len=%d",
             role, model, timeout, len(payload.get("command", "")))
    t0 = time.time()
    try:
        # start_new_session -> own process group, so a timeout can SIGKILL the whole
        # tree (claude spawns shells/servers/git that would otherwise orphan).
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, cwd=str(WORKSPACE), start_new_session=True)
    except FileNotFoundError:
        return {"success": False, "error": f"claude binary not found: {CLAUDE_BIN}"}
    try:
        stdout, stderr = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            pass
        try:
            stdout, stderr = p.communicate(timeout=5)  # reap + collect partial output
        except Exception:  # noqa: BLE001 — best-effort reap
            stdout, stderr = "", ""
        return {"success": False, "error": f"timeout after {timeout}s",
                "stderr": (stderr or "")[-400:], "partial": (stdout or "")[:2000],
                "duration_s": round(time.time() - t0, 1)}
    dur = round(time.time() - t0, 1)
    rc = p.returncode
    err_tail = (stderr or "")[-400:]
    if rc != 0:
        log.error("claude exit=%s stderr=%s", rc, err_tail)
        return {"success": False, "error": f"claude exit {rc}",
                "stderr": err_tail, "duration_s": dur}
    log.info("claude rc=0 dur=%ss stderr_tail=%s", dur, err_tail)  # log stderr even on success
    cost, is_err, subtype = None, False, None
    try:
        out = json.loads(stdout)
    except json.JSONDecodeError:
        out = None
    if isinstance(out, dict):
        text = out.get("result", "")
        cost = out.get("total_cost_usd")
        is_err = bool(out.get("is_error"))
        subtype = out.get("subtype")
    else:
        text = (stdout or "")[:8000]  # raw-text fallback (non-json or non-dict json)
    if is_err or not (text or "").strip():
        reason = (subtype or "is_error") if is_err else "empty result"
        return {"success": False,
                "error": f"claude returned no usable result ({reason})",
                "response": text, "cost_usd": cost, "duration_s": dur}
    return {"success": True, "response": text, "cost_usd": cost, "duration_s": dur}


def post_callback(url: str, body: dict) -> bool:
    """POST the callback with retries; return True if delivered, else False."""
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    for attempt, delay in ((1, 0), (2, 5), (3, 15)):
        if delay:
            time.sleep(delay)
        try:
            req = urllib.request.Request(
                url, data=data, method="POST",
                headers={"Content-Type": "application/json",
                         "X-SOFI-Token": TOKEN})
            with urllib.request.urlopen(req, timeout=30) as r:
                log.info("callback %s -> %s (attempt %d)", url, r.status, attempt)
                return True
        except Exception as e:  # noqa: BLE001 — network layer, log and retry
            log.warning("callback attempt %d failed: %s", attempt, e)
    log.error("callback gave up: %s", url)
    return False


def worker() -> None:
    while True:
        payload, job = WORK_Q.get()
        jid = job["job_id"]
        try:
            JOBS.update(jid, status="running", started=now_iso())
            timeout = coerce_timeout(payload.get("timeout", ASYNC_TIMEOUT_DEFAULT),
                                     ASYNC_TIMEOUT_DEFAULT, ASYNC_TIMEOUT_MAX)
            result = run_claude(payload, payload["_role"], timeout)
            status = "done" if result.get("success") else "failed"
            JOBS.update(jid, status=status, finished=now_iso(),
                        result=result.get("response"), error=result.get("error"))
            cb = payload.get("callback_url")
            cb_status = "none"
            if cb:
                cb_body = {
                    "job_id": jid, "status": status,
                    "response": result.get("response"), "error": result.get("error"),
                    "meta": payload.get("meta"), "role": payload["_role"],
                    "duration_s": result.get("duration_s"),
                }
                delivered = post_callback(cb, cb_body)
                cb_status = "delivered" if delivered else "failed"
                if not delivered:
                    deadletter({**cb_body, "callback_url": cb, "ts": now_iso()})
            JOBS.update(jid, callback_status=cb_status)
            final = JOBS.get(jid) or dict(job)
            persist({**final, "cost_usd": result.get("cost_usd"),
                     "duration_s": result.get("duration_s")})
        except Exception as e:  # noqa: BLE001 — a bad job must never kill the worker
            log.exception("worker job %s crashed", jid)
            JOBS.update(jid, status="failed", finished=now_iso(), error=str(e))
            cb = payload.get("callback_url")
            cb_status = "none"
            if cb:
                cb_body = {"job_id": jid, "status": "failed", "response": None,
                           "error": str(e), "meta": payload.get("meta"),
                           "role": payload.get("_role")}
                delivered = post_callback(cb, cb_body)
                cb_status = "delivered" if delivered else "failed"
                if not delivered:
                    deadletter({**cb_body, "callback_url": cb, "ts": now_iso()})
            failed = JOBS.get(jid) or dict(job)
            persist({**failed, "callback_status": cb_status, "error": str(e)})
        finally:
            WORK_Q.task_done()


# ───────────────────────── rate limit ─────────────────────────

_rate_lock = threading.Lock()
_rate_window: list[float] = []


def rate_ok() -> bool:
    now = time.time()
    with _rate_lock:
        while _rate_window and now - _rate_window[0] > 60:
            _rate_window.pop(0)
        if len(_rate_window) >= RATE_LIMIT_PER_MIN:
            return False
        _rate_window.append(now)
        return True


# ───────────────────────── http ─────────────────────────

class Handler(BaseHTTPRequestHandler):
    server_version = "sofi-gateway/2.0"
    timeout = 30  # socket read timeout — drop slow/stuck clients

    def _send(self, code: int, body: dict) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *_):
        pass

    def _authed(self) -> bool:
        supplied = self.headers.get("X-SOFI-Token", "")
        return bool(TOKEN) and hmac.compare_digest(supplied, TOKEN)

    def _log_auth_fail(self) -> None:
        log.warning("auth fail from %s path=%s ua=%s", self.client_address[0],
                    self.path, self.headers.get("User-Agent", "-"))

    def do_GET(self):
        path = urllib.parse.urlsplit(self.path).path  # strip query, exact match
        if path == "/healthz":
            return self._send(200, {"status": "ok", "service": "sofi-gateway",
                                    "version": 2, "queue": WORK_Q.qsize()})
        if not self._authed():
            self._log_auth_fail()
            return self._send(401, {"error": "unauthorized"})
        if path.startswith("/job/"):
            job = JOBS.get(path[5:])
            return self._send(200 if job else 404, job or {"error": "no such job"})
        if path == "/jobs":
            return self._send(200, {"jobs": JOBS.recent()})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        path = urllib.parse.urlsplit(self.path).path  # strip query, exact match
        if path != "/dispatch":
            return self._send(404, {"error": "not found"})
        if not self._authed():
            self._log_auth_fail()
            return self._send(401, {"error": "unauthorized"})
        try:
            length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            return self._send(400, {"error": "bad content-length"})
        if length < 0:
            return self._send(400, {"error": "bad content-length"})
        if length > MAX_BODY:
            return self._send(413, {"error": "body too large"})
        try:
            payload = json.loads(self.rfile.read(length) if length else b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"error": "invalid json"})
        if not isinstance(payload, dict):
            return self._send(400, {"error": "body must be a json object"})

        if "timeout" in payload and not timeout_coercible(payload["timeout"]):
            return self._send(400, {"error": "invalid timeout"})
        command = (payload.get("command") or "").strip()
        if not command:
            return self._send(400, {"error": "missing command"})
        role = resolve_agent(payload.get("role") or "sofi-ceo")
        if not role:
            return self._send(404, {"error": f"unknown agent: {payload.get('role')}"})
        model = payload.get("model", MODEL_DEFAULT)
        if model not in MODEL_ALLOW:
            return self._send(400, {"error": f"model not allowed: {model}"})

        # callback SSRF/token-leak guard — never POST the token to an unknown host
        cb = payload.get("callback_url")
        if cb:
            host = urllib.parse.urlsplit(cb).netloc.rsplit("@", 1)[-1]  # strip userinfo
            if host not in CALLBACK_ALLOW:
                return self._send(400, {"error": f"callback host not allowed: {host}"})

        # defense-in-depth owner gate for whatsapp sources (n8n stays the primary gate)
        source = payload.get("source", "n8n")
        if isinstance(source, str) and source.startswith("whatsapp"):
            if OWNER_CHAT:
                meta = payload.get("meta")
                if not isinstance(meta, dict) or meta.get("chatId") != OWNER_CHAT:
                    return self._send(403, {"error": "forbidden: owner mismatch"})
            else:
                log.warning("owner-gate disabled: SOFI_OWNER_CHAT unset "
                            "(source=%s) — relying on n8n filter", source)

        if not rate_ok():
            return self._send(429, {"error": "rate limit — max "
                                    f"{RATE_LIMIT_PER_MIN}/min"})
        payload["_role"] = role
        mode = payload.get("mode", "async")

        if mode == "sync":
            if not SYNC_SEM.acquire(blocking=False):  # cap concurrent in-thread runs
                return self._send(503, {"error": "busy"})
            try:
                timeout = coerce_timeout(payload.get("timeout", SYNC_TIMEOUT),
                                         SYNC_TIMEOUT, SYNC_TIMEOUT)
                job = JOBS.create(payload, "sync")
                JOBS.update(job["job_id"], status="running", started=now_iso())
                result = run_claude(payload, role, timeout)
                status = "done" if result.get("success") else "failed"
                JOBS.update(job["job_id"], status=status, finished=now_iso(),
                            result=result.get("response"), error=result.get("error"))
                final = JOBS.get(job["job_id"]) or job
                persist({**final, "cost_usd": result.get("cost_usd"),
                         "duration_s": result.get("duration_s")})
                return self._send(200 if result.get("success") else 500,
                                  {"job_id": job["job_id"], **result})
            finally:
                SYNC_SEM.release()

        job = JOBS.create(payload, "async")
        try:
            WORK_Q.put_nowait((payload, job))
        except queue.Full:
            JOBS.update(job["job_id"], status="failed", finished=now_iso(),
                        error="queue full")
            persist(JOBS.get(job["job_id"]) or job)
            return self._send(503, {"error": "queue full"})
        return self._send(202, {"job_id": job["job_id"], "status": "queued",
                                "poll": f"/job/{job['job_id']}"})


def main() -> None:
    if not TOKEN:
        raise SystemExit("SOFI_GATEWAY_TOKEN not set — refusing to start without auth")
    for _ in range(MAX_WORKERS):
        threading.Thread(target=worker, daemon=True).start()
    log.info("gateway v2 on %s:%s workers=%d sync_slots=%d owner_gate=%s",
             BIND, PORT, MAX_WORKERS, SYNC_SLOTS, "on" if OWNER_CHAT else "off")
    ThreadingHTTPServer((BIND, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
