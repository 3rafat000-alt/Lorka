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
  - role allowlist = .claude/agents/*.md ; model allowlist fixed
  - body cap 256 KiB; global rate limit (loop protection)
  - every job persisted to ~/.sofi-run/gateway-jobs.jsonl (audit trail)

Owner: devops-cloud-lead. Gate: tool-plane (not a project).
"""
from __future__ import annotations

import hmac
import json
import logging
import os
import queue
import subprocess
import threading
import time
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

MODEL_ALLOW = {"haiku", "sonnet", "opus", "claude-fable-5", "fable"}
MODEL_DEFAULT = "haiku"

RUN_DIR = Path.home() / ".sofi-run"
LOG_DIR = RUN_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
JOBS_FILE = RUN_DIR / "gateway-jobs.jsonl"

logging.basicConfig(
    filename=str(LOG_DIR / "sofi-gateway.log"), level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("sofi-gateway")


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


# ───────────────────────── agents / RCCF ─────────────────────────

def resolve_agent(role: str) -> str | None:
    """Return the canonical agent name if the spec exists, else None."""
    agents = WORKSPACE / ".claude" / "agents"
    for cand in (f"{role}.md", f"sofi-{role}.md"):
        if (agents / cand).is_file():
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
            "role": payload.get("role"), "project": payload.get("project", "PRJ-SAKK"),
            "command": payload.get("command", "")[:500],
            "source": payload.get("source", "n8n"),
            "meta": payload.get("meta"), "created": now_iso(),
            "started": None, "finished": None, "result": None, "error": None,
        }
        with self._lock:
            self._jobs[jid] = job
            self._order.append(jid)
            while len(self._order) > JOBS_KEEP:
                self._jobs.pop(self._order.pop(0), None)
        return job

    def get(self, jid: str) -> dict | None:
        with self._lock:
            return self._jobs.get(jid)

    def update(self, jid: str, **kv) -> None:
        with self._lock:
            if jid in self._jobs:
                self._jobs[jid].update(kv)

    def recent(self, limit: int = 20) -> list[dict]:
        with self._lock:
            return [self._jobs[j] for j in self._order[-limit:]][::-1]


JOBS = Jobs()
WORK_Q: "queue.Queue[tuple[dict, dict]]" = queue.Queue(maxsize=50)


def persist(job: dict) -> None:
    try:
        with open(JOBS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(job, ensure_ascii=False) + "\n")
    except OSError as e:
        log.error("persist failed: %s", e)


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
        res = subprocess.run(cmd, capture_output=True, text=True,
                             timeout=timeout, cwd=str(WORKSPACE))
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"timeout after {timeout}s"}
    except FileNotFoundError:
        return {"success": False, "error": f"claude binary not found: {CLAUDE_BIN}"}
    dur = round(time.time() - t0, 1)
    if res.returncode != 0:
        log.error("claude exit=%s stderr=%s", res.returncode, res.stderr[:400])
        return {"success": False, "error": f"claude exit {res.returncode}",
                "stderr": res.stderr[:400], "duration_s": dur}
    try:
        out = json.loads(res.stdout)
        text = out.get("result", "")
        cost = out.get("total_cost_usd")
    except json.JSONDecodeError:
        text, cost = res.stdout[:8000], None
    return {"success": True, "response": text, "cost_usd": cost, "duration_s": dur}


def post_callback(url: str, body: dict) -> None:
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
                return
        except Exception as e:  # noqa: BLE001 — network layer, log and retry
            log.warning("callback attempt %d failed: %s", attempt, e)
    log.error("callback gave up: %s", url)


def worker() -> None:
    while True:
        payload, job = WORK_Q.get()
        jid = job["job_id"]
        JOBS.update(jid, status="running", started=now_iso())
        timeout = min(int(payload.get("timeout", ASYNC_TIMEOUT_DEFAULT)), ASYNC_TIMEOUT_MAX)
        result = run_claude(payload, payload["_role"], timeout)
        status = "done" if result.get("success") else "failed"
        JOBS.update(jid, status=status, finished=now_iso(),
                    result=result.get("response"), error=result.get("error"))
        final = JOBS.get(jid) or job
        persist({**final, "cost_usd": result.get("cost_usd"),
                 "duration_s": result.get("duration_s")})
        cb = payload.get("callback_url")
        if cb:
            post_callback(cb, {
                "job_id": jid, "status": status,
                "response": result.get("response"), "error": result.get("error"),
                "meta": payload.get("meta"), "role": payload["_role"],
                "duration_s": result.get("duration_s"),
            })
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

    def do_GET(self):
        if self.path == "/healthz":
            return self._send(200, {"status": "ok", "service": "sofi-gateway",
                                    "version": 2, "queue": WORK_Q.qsize()})
        if not self._authed():
            return self._send(401, {"error": "unauthorized"})
        if self.path.startswith("/job/"):
            job = JOBS.get(self.path[5:])
            return self._send(200 if job else 404, job or {"error": "no such job"})
        if self.path.startswith("/jobs"):
            return self._send(200, {"jobs": JOBS.recent()})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/dispatch":
            return self._send(404, {"error": "not found"})
        if not self._authed():
            log.warning("auth fail from %s", self.client_address[0])
            return self._send(401, {"error": "unauthorized"})
        length = int(self.headers.get("Content-Length", 0))
        if length > MAX_BODY:
            return self._send(413, {"error": "body too large"})
        try:
            payload = json.loads(self.rfile.read(length) if length else b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"error": "invalid json"})

        command = (payload.get("command") or "").strip()
        if not command:
            return self._send(400, {"error": "missing command"})
        role = resolve_agent(payload.get("role") or "sofi-ceo")
        if not role:
            return self._send(404, {"error": f"unknown agent: {payload.get('role')}"})
        model = payload.get("model", MODEL_DEFAULT)
        if model not in MODEL_ALLOW:
            return self._send(400, {"error": f"model not allowed: {model}"})
        if not rate_ok():
            return self._send(429, {"error": "rate limit — max "
                                    f"{RATE_LIMIT_PER_MIN}/min"})
        payload["_role"] = role
        mode = payload.get("mode", "async")

        if mode == "sync":
            timeout = min(int(payload.get("timeout", SYNC_TIMEOUT)), SYNC_TIMEOUT)
            job = JOBS.create(payload, "sync")
            JOBS.update(job["job_id"], status="running", started=now_iso())
            result = run_claude(payload, role, timeout)
            status = "done" if result.get("success") else "failed"
            JOBS.update(job["job_id"], status=status, finished=now_iso(),
                        result=result.get("response"), error=result.get("error"))
            persist(JOBS.get(job["job_id"]) or job)
            return self._send(200 if result.get("success") else 500,
                              {"job_id": job["job_id"], **result})

        job = JOBS.create(payload, "async")
        try:
            WORK_Q.put_nowait((payload, job))
        except queue.Full:
            JOBS.update(job["job_id"], status="failed", error="queue full")
            return self._send(503, {"error": "queue full"})
        return self._send(202, {"job_id": job["job_id"], "status": "queued",
                                "poll": f"/job/{job['job_id']}"})


def main() -> None:
    if not TOKEN:
        raise SystemExit("SOFI_GATEWAY_TOKEN not set — refusing to start without auth")
    for _ in range(MAX_WORKERS):
        threading.Thread(target=worker, daemon=True).start()
    log.info("gateway v2 on %s:%s workers=%d", BIND, PORT, MAX_WORKERS)
    ThreadingHTTPServer((BIND, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
