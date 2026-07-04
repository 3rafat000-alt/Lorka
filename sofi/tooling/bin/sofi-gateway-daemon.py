#!/usr/bin/env python3
"""SOFI Gateway Daemon — n8n ↔ Claude Code CLI bridge.

Listens on 127.0.0.1:8099. Receives RCCF blocks from n8n workflows over HTTP POST /dispatch,
spawns Claude with the block, returns JSON result. No mounts, no Docker — host-side daemon
with full access to claude CLI, git, and workspace.

Owner: devops-cloud-lead. Gate: 6-7.
"""
import json
import os
import subprocess
import logging
import hashlib
import hmac
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WORKSPACE = Path(os.environ.get("SOFI_WORKSPACE", "/home/es3dlll/Desktop/Lorka"))
BIND = os.environ.get("SOFI_GATEWAY_BIND", "127.0.0.1")
PORT = int(os.environ.get("SOFI_GATEWAY_PORT", "8099"))
TOKEN = os.environ.get("SOFI_GATEWAY_TOKEN", "")
TIMEOUT = 300  # 5m per dispatch

LOG_DIR = WORKSPACE / ".sofi-run" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "sofi-gateway.log"

logging.basicConfig(
    filename=str(LOG_FILE), level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("sofi-gateway")


def resolve_agent(role: str) -> Path | None:
    """Find agent spec in .claude/agents/sofi-<name>.md."""
    if not role:
        return None
    candidates = [
        WORKSPACE / ".claude" / "agents" / f"{role}.md",
        WORKSPACE / ".claude" / "agents" / f"sofi-{role}.md",
    ]
    for path in candidates:
        if path.is_file():
            return path
    for path in (WORKSPACE / ".claude" / "agents").glob(f"*{role}*.md"):
        return path
    return None


def build_rccf(payload: dict) -> str:
    """Construct RCCF prompt from dispatch payload."""
    role = payload.get("role", "unknown")
    project = payload.get("project", "PRJ-SAKK")
    command = payload.get("command", "")
    context = payload.get("context", "")
    fmt = payload.get("format", "artifact")
    priority = payload.get("priority", "medium")

    head_sha = "unknown"
    state_file = WORKSPACE / "projects" / project / "_context" / "STATE.md"
    if state_file.is_file():
        try:
            for line in state_file.read_text(encoding="utf-8", errors="ignore").splitlines():
                if line.startswith("head_sha:"):
                    head_sha = line.split(":", 1)[1].strip().split()[0]
                    break
        except Exception:
            pass

    return (
        f"🎭 **Role:** {role}\n"
        f"📂 **Context:**\n"
        f"- Project: {project}\n"
        f"- HEAD: {head_sha}\n"
        f"- Priority: {priority}\n"
        f"- Source: {payload.get('source', 'n8n-orchestrator')}\n"
        f"- Trigger: {payload.get('trigger', 'unknown')}\n"
        f"{('- Extra: ' + context + chr(10)) if context else ''}"
        f"\n"
        f"🎯 **Command:**\n{command}\n"
        f"\n"
        f"📐 **Format:**\n{fmt}\n"
    )


def dispatch(payload: dict) -> dict:
    """Execute Claude with RCCF block."""
    role = payload.get("role", "")
    if not role or not payload.get("command"):
        return {"success": False, "error": "missing role or command"}

    agent_spec = resolve_agent(role)
    if not agent_spec:
        return {"success": False, "error": f"agent not found: {role}"}

    rccf = build_rccf(payload)
    log.info(f"dispatch role={role} command_len={len(payload.get('command', ''))} chars")

    try:
        result = subprocess.run(
            ["claude", "-p", rccf, "--model", payload.get("model", "haiku")],
            capture_output=True, text=True, timeout=TIMEOUT, cwd=str(WORKSPACE),
        )
    except subprocess.TimeoutExpired:
        log.error(f"timeout: {role}")
        return {"success": False, "error": f"timeout after {TIMEOUT}s"}
    except Exception as e:
        log.error(f"dispatch failed: {e}")
        return {"success": False, "error": str(e)[:200]}

    if result.returncode != 0:
        log.error(f"exit {result.returncode}: {result.stderr[:300]}")
        return {"success": False, "error": f"exit {result.returncode}"}

    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError:
        parsed = {"response": result.stdout[:4000]}

    return {
        "success": True,
        "response": parsed.get("response", ""),
        "artifact": parsed.get("artifact", ""),
        "role": role,
        "ts": datetime.now(timezone.utc).isoformat(),
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: dict):
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_):
        pass  # suppress stdlib logs

    def do_GET(self):
        if self.path == "/healthz":
            self._send(200, {"status": "ok", "service": "sofi-gateway"})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/dispatch":
            return self._send(404, {"error": "not found"})

        # Auth
        supplied_token = self.headers.get("X-SOFI-Token", "")
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return self._send(400, {"success": False, "error": "invalid json"})

        # Check token (from header or body)
        final_token = supplied_token or payload.get("token", "")
        if TOKEN and final_token != TOKEN:
            log.warning(f"auth fail from {self.client_address[0]}")
            return self._send(401, {"success": False, "error": "unauthorized"})

        result = dispatch(payload)
        self._send(200 if result.get("success") else 500, result)


def main():
    log.info(f"SOFI Gateway Daemon starting on {BIND}:{PORT}")
    server = ThreadingHTTPServer((BIND, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("shutdown")


if __name__ == "__main__":
    main()
