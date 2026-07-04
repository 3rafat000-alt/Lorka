#!/usr/bin/env python3
"""SOFI AI — Pre-tool security gate (harvested + adapted from the old SOFI Engineering team).

Enforces the doctrine "full access, but NO dangerous commands" at the HARNESS level —
complements the Python `guard.py` (which only governs sofi_tools scripts). This gate
runs on every tool call:
 • blocks destructive shell/git commands (force-push, history rewrite, mass delete…)
 • protects secrets (.env reads/writes; warns on secrets pasted into code)
 • audits every block to .claude/memory/audit.jsonl

Fails OPEN: any internal error → allow (never break the workflow).
Code & security stay normal — this file is real defense, never compressed away.
"""
import json
import sys
import re
from datetime import datetime, timezone
from pathlib import Path

# (regex on a lowercased, whitespace-normalized command, human-readable reason)
DANGEROUS = [
    # —— filesystem / system ——
    (r'\brm\s+-[a-z]*r[a-z]*f\b\s+(-[a-z]+\s+)*(/|~|\$home|\.\.?|\*)(\s|/|$)', "catastrophic recursive delete (rm -rf on /, ~, ., *)"),
    (r'\bsudo\b', "privilege escalation (sudo) is forbidden for agents"),
    (r'\bmkfs\b|\bdd\b\s+if=.*of=/dev/|>\s*/dev/sd', "raw disk write / format"),
    (r'\bchmod\s+(-r\s+)?777\s+/|\bchmod\s+-r\s+777\b', "chmod 777 hazard"),
    (r':\(\)\s*\{\s*:\s*\|\s*:', "fork bomb"),
    # —— git: history / force / destructive ——
    (r'\bgit\s+push\b.*(--force(?!-with-lease)|\s-f(\s|$))', "git push --force (rewrites remote history)"),
    (r'\bgit\s+reset\s+--hard\b', "git reset --hard (loses uncommitted work)"),
    (r'\bgit\s+clean\s+-[a-z]*f', "git clean -f (deletes untracked files)"),
    (r'\bgit\s+checkout\s+(--\s+)?\.(\s|$)', "git checkout . (discards all changes)"),
    (r'\bgit\s+restore\s+(--[a-z]+\s+)*\.(\s|$)', "git restore . (discards all changes)"),
    (r'\bgit\s+(filter-branch|filter-repo)\b', "git history rewrite"),
    (r'\bgit\s+reflog\s+expire\b|\bgit\s+gc\s+--prune', "destroys the recovery reflog"),
    (r'\bgit\s+update-ref\s+-d\b', "deletes a git ref"),
    (r'\bgit\s+push\s+\S+\s+(--delete|:)', "deletes a remote branch/tag"),
    (r'\bgit\s+branch\s+-d\s+(main|master|develop)\b', "deletes a protected branch"),
    (r'\bgit\s+tag\s+-d\b', "deletes a tag"),
]

SECRET_PATTERNS = [
    r'(?i)(password|secret|api[_-]?key|api[_-]?secret|access[_-]?key|token)\s*[=:]\s*["\']?[A-Za-z0-9/\+_\-]{12,}',
]

# —— Git discipline (engine/protocols/git-discipline.md) — enforced at commit time ——
# Commit subjects MUST start with a Conventional-Commit type.
CONVENTIONAL = re.compile(
    r'^(feat|fix|chore|docs|refactor|test|perf|ci|build|style|revert|wip)'
    r'(\([\w./-]+\))?!?:\s+\S'
)
# Paths that must never be staged/committed (defense beyond .gitignore).
FORBIDDEN_PATH = re.compile(
    r'(_scratch/|\.gstack/|__pycache__/|'
    r'\.env\.(bak|vault|testing)\b|(?<![\w.])\.env(\s|$|/)|'
    r'\baudit\.jsonl\b|\.(pem|key|p12|pfx|keystore|jks)\b)'
)
# Extract the first -m / --message value (quoted or single token).
_MSG = re.compile(r'(?:-m|--message)(?:=|\s+)("([^"]*)"|\'([^\']*)\'|(\S+))')


def match_danger(command: str):
    norm = ' '.join(command.lower().split())
    for pat, reason in DANGEROUS:
        if re.search(pat, norm):
            return reason
    return None


def check_commit(command: str):
    """Block a malformed or unsafe commit/stage. Returns a reason or None.
    Only `git commit` with an inline -m is format-checked; editor commits pass
    through (git-check / review catch those). Fails open on any ambiguity."""
    norm = ' '.join(command.split())
    is_commit = re.search(r'\bgit\s+commit\b', norm) is not None
    is_stage = re.search(r'\bgit\s+(add|stage)\b', norm) is not None
    if not (is_commit or is_stage):
        return None
    # Never stage/commit a forbidden path named explicitly on the command line.
    # (.env.example is allowed — the pattern only matches secret/runtime variants.)
    if FORBIDDEN_PATH.search(norm) and not re.search(r'\.env\.example\b', norm):
        return "stages a secret / runtime / _scratch path (git-discipline §7) — never commit it"
    if is_commit:
        m = _MSG.search(command)
        if m:
            msg = next(g for g in m.groups()[1:] if g is not None)
            # Can't statically verify a dynamically-built message ($(...), `...`, $VAR,
            # or a heredoc/-F file) — fail open; `sofi checkpoint` is the enforced path.
            if msg.lstrip().startswith(('$', '`')) or '-F' in norm or '--file' in norm:
                return None
            if not CONVENTIONAL.match(msg):
                return ("commit message must start with a type "
                        "(feat|fix|chore|docs|refactor|test|perf|ci|build|style|revert|wip): … "
                        "— see git-discipline.md §4")
    return None


def record_block(agent_type, command, reason):
    try:
        AUDIT.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent_type or "system",
            "office": "security",
            "action": "security.block",
            "summary": f"🛡️ Dangerous command blocked: {reason}",
            "details": {"command": command[:200], "reason": reason},
            "tags": ["security", "blocked", "git-guard"], "priority": "high",
        }
        with open(AUDIT, 'a') as f:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')
    except Exception:
        pass


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    try:
        tool = data.get('tool_name', '')
        inp = data.get('tool_input', {}) or {}
        agent_type = data.get('agent_type')

        # protect .env (read/edit/write) — allow .env.example
        if tool in ('Read', 'Edit', 'Write'):
            path = inp.get('file_path', inp.get('filePath', '')) or ''
            if re.search(r'(^|/)\.env(\.|$)', path) and not path.endswith('.env.example'):
                print("BLOCKED: reading/writing .env is not allowed — use .env.example", file=sys.stderr)
                record_block(agent_type, f"{tool} {path}", "access .env")
                sys.exit(2)

        # block dangerous shell/git commands
        if tool == 'Bash':
            cmd = inp.get('command', '') or ''
            reason = match_danger(cmd)
            if reason:
                print(f"BLOCKED by SOFI AI security policy: {reason}\nCommand refused. For a rare exception, run it manually outside the agent.", file=sys.stderr)
                record_block(agent_type, cmd, reason)
                sys.exit(2)
            # enforce git discipline (commit format + no forbidden paths)
            greason = check_commit(cmd)
            if greason:
                print(f"BLOCKED by SOFI git discipline: {greason}\nUse `sofi checkpoint <PRJ> \"<type>(<scope>): <subject>\"` for a compliant, traceable commit.", file=sys.stderr)
                record_block(agent_type, cmd, greason)
                sys.exit(2)

        # warn (not block) on secrets pasted into code
        if tool in ('Write', 'Edit'):
            content = inp.get('content', inp.get('new_string', inp.get('newString', '')))
            if isinstance(content, str) and len(content) < 200000:
                if any(re.search(p, content) for p in SECRET_PATTERNS):
                    print("WARNING: this code may contain a secret/key — verify before continuing", file=sys.stderr)

        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == '__main__':
    main()
