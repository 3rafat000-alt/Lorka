#!/usr/bin/env python3
"""gitflow.py — the Autonomous Git Guard helper for SOFI AI.

A thin, guard-railed wrapper over `git` and `gh` (both invoked via subprocess)
that lets agents create feature branches, conventional commits, and PRs SAFELY.

It does NOT replace the repo's existing pre/post_tool_use.py hooks — it
complements them. Every dangerous action is refused up front (exit 2) instead of
being executed and cleaned up afterwards.

STDLIB ONLY. One JSON object to stdout with --json. Exit codes:
  0  ok
  1  git/gh failure
  2  usage error OR guard-refusal (a blocked dangerous action)
No traceback ever leaks to the user.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
ROOT = Path(os.environ.get("SOFI_HOME") or Path(__file__).resolve().parents[3])

PROTECTED = {"main", "master", "prod", "production"}
COMMIT_TYPES = ("feat", "fix", "docs", "refactor", "test", "chore", "perf", "build", "ci")
BRANCH_RE = re.compile(r"^[a-z0-9][a-z0-9._/-]{1,60}$")
SUBJECT_MAX = 72
TAIL_LINES = 30

COAUTHOR = "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
PR_FOOTER = "🤖 Generated with [Claude Code](https://claude.com/claude-code)"


# --------------------------------------------------------------------------- #
# Subprocess helpers — always a list, never shell=True
# --------------------------------------------------------------------------- #
def _tail(text, n=TAIL_LINES):
    if not text:
        return ""
    return "\n".join(text.splitlines()[-n:])


def _run(argv):
    """Run a command list in ROOT, capture text. Returns (rc, stdout, stderr)."""
    try:
        proc = subprocess.run(argv, cwd=str(ROOT), capture_output=True, text=True)
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError as exc:
        return 127, "", f"{argv[0]}: not found ({exc})"
    except OSError as exc:  # pragma: no cover - defensive
        return 127, "", str(exc)


def _git(args):
    return _run(["git"] + list(args))


def _gh(args):
    return _run(["gh"] + list(args))


def _cmd_result(argv, rc, out, err):
    """Structured record of the exact command run + returncode + output tails."""
    return {
        "command": " ".join(argv),
        "returncode": rc,
        "stdout": _tail(out),
        "stderr": _tail(err),
    }


# --------------------------------------------------------------------------- #
# Repo introspection
# --------------------------------------------------------------------------- #
def _current_branch():
    rc, out, _ = _git(["rev-parse", "--abbrev-ref", "HEAD"])
    if rc != 0:
        return None
    name = out.strip()
    return name or None


def _is_dirty():
    rc, out, _ = _git(["status", "--porcelain"])
    if rc != 0:
        return False
    return bool(out.strip())


def _ahead_behind():
    # left = HEAD side (ahead), right = upstream side (behind)
    rc, out, _ = _git(["rev-list", "--left-right", "--count", "HEAD...@{upstream}"])
    if rc != 0 or not out.strip():
        return None, None
    parts = out.split()
    if len(parts) != 2:
        return None, None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None, None


def _head_sha():
    rc, out, _ = _git(["rev-parse", "HEAD"])
    return out.strip() if rc == 0 else None


# --------------------------------------------------------------------------- #
# Pure guard logic (shared by guard-check subcommand + selftest)
# --------------------------------------------------------------------------- #
def guard_check(cmd_string, current_branch=None):
    """Match a proposed git command string against the deny rules.

    Returns (allowed: bool, reason: str). Pure logic — never executes anything.
    """
    toks = cmd_string.split()

    # history / worktree destruction
    if "reset" in toks and "--hard" in toks:
        return False, "git reset --hard is forbidden (destroys worktree/history)"
    if "clean" in toks and any(
        t.startswith("-") and "f" in t.lstrip("-") for t in toks
    ):
        return False, "git clean -f… is forbidden (deletes untracked files)"
    if "filter-branch" in toks or (
        "rebase" in toks and ("-i" in toks or "--interactive" in toks)
    ):
        return False, "history rewrite is forbidden"

    # force push / any force flag
    if "--force" in toks or "--force-with-lease" in toks or "-f" in toks:
        return False, "force flag is forbidden (never force-push)"

    # protected-branch push/commit
    if current_branch and current_branch.strip() in PROTECTED:
        if "push" in toks or "commit" in toks:
            return False, f"operation on protected branch '{current_branch}' is forbidden"

    return True, "allowed"


def build_subject(ctype, scope, message):
    """Build a Conventional Commit subject.

    Returns (subject: str|None, error: str|None).
    """
    if ctype not in COMMIT_TYPES:
        return None, "invalid type '%s' (allowed: %s)" % (ctype, ",".join(COMMIT_TYPES))
    message = (message or "").strip()
    if not message:
        return None, "empty commit message"
    scope = (scope or "").strip()
    subject = "%s(%s): %s" % (ctype, scope, message) if scope else "%s: %s" % (ctype, message)
    if len(subject) > SUBJECT_MAX:
        return None, "subject exceeds %d chars (%d)" % (SUBJECT_MAX, len(subject))
    return subject, None


# --------------------------------------------------------------------------- #
# Subcommand handlers — each returns (obj: dict, exit_code: int)
# --------------------------------------------------------------------------- #
def cmd_current(_args):
    branch = _current_branch()
    if branch is None:
        return {"ok": False, "error": "not a git repository or no HEAD"}, 1
    ahead, behind = _ahead_behind()
    return {
        "ok": True,
        "branch": branch,
        "dirty": _is_dirty(),
        "ahead": ahead,
        "behind": behind,
        "protected": branch in PROTECTED,
    }, 0


def cmd_branch(args):
    name = args.name
    if name in PROTECTED or name in {"main", "master"}:
        return {"ok": False, "blocked": "cannot create/switch to protected branch '%s'" % name}, 2
    if not BRANCH_RE.match(name):
        return {"ok": False, "blocked": "invalid branch name '%s' (must match %s)" % (name, BRANCH_RE.pattern)}, 2

    argv = ["git", "switch", "-c", name]
    rc, out, err = _run(argv)
    if rc != 0:
        # fallback for older git without `switch`
        fb = ["git", "checkout", "-b", name]
        frc, fout, ferr = _run(fb)
        if frc == 0:
            res = _cmd_result(fb, frc, fout, ferr)
            return {"ok": True, "branch": name, "created": True, **res}, 0
        res = _cmd_result(argv, rc, out, err)
        return {"ok": False, "error": "failed to create branch '%s'" % name, **res}, 1

    res = _cmd_result(argv, rc, out, err)
    return {"ok": True, "branch": name, "created": True, **res}, 0


def cmd_commit(args):
    branch = _current_branch()
    if branch and branch in PROTECTED:
        return {"ok": False, "blocked": "refuse to commit on protected branch '%s'" % branch}, 2

    subject, err = build_subject(args.type, args.scope, args.message)
    if subject is None:
        return {"ok": False, "blocked": err}, 2

    if args.all:
        arc, aout, aerr = _git(["add", "-A"])
        if arc != 0:
            return {"ok": False, "error": "git add -A failed", **_cmd_result(["git", "add", "-A"], arc, aout, aerr)}, 1

    msg_args = ["-m", subject]
    if args.body:
        msg_args += ["-m", args.body]
    msg_args += ["-m", COAUTHOR]

    argv = ["git", "commit"] + msg_args
    rc, out, err = _run(argv)
    res = _cmd_result(argv, rc, out, err)
    if rc != 0:
        return {"ok": False, "error": "commit failed (nothing staged?)", "subject": subject, **res}, 1
    return {"ok": True, "branch": branch, "subject": subject, "head_sha": _head_sha(), **res}, 0


def cmd_push(args):
    branch = _current_branch()
    if branch is None:
        return {"ok": False, "error": "cannot determine current branch"}, 1
    if branch in PROTECTED:
        return {"ok": False, "blocked": "refuse to push protected branch '%s'" % branch}, 2

    argv = ["git", "push"]
    if args.set_upstream:
        argv += ["--set-upstream", "origin", branch]
    # NEVER a force flag — by construction.
    rc, out, err = _run(argv)
    res = _cmd_result(argv, rc, out, err)
    if rc != 0:
        return {"ok": False, "error": "push failed", "branch": branch, **res}, 1
    return {"ok": True, "branch": branch, **res}, 0


def cmd_pr(args):
    branch = _current_branch()
    if branch is None:
        return {"ok": False, "error": "cannot determine current branch (head)"}, 1
    base = (args.base or "main").strip()
    if branch == base:
        return {"ok": False, "blocked": "PR head '%s' equals base '%s'" % (branch, base)}, 2

    body = (args.body or "").rstrip()
    body = (body + "\n\n" + PR_FOOTER) if body else PR_FOOTER

    argv = ["gh", "pr", "create", "--title", args.title, "--body", body,
            "--base", base, "--head", branch]
    if args.draft:
        argv.append("--draft")

    rc, out, err = _run(argv)
    res = _cmd_result(argv, rc, out, err)
    if rc != 0:
        return {"ok": False, "error": "gh pr create failed", "head": branch, "base": base, **res}, 1

    url = ""
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("http"):
            url = line
    return {"ok": True, "head": branch, "base": base, "draft": bool(args.draft), "url": url, **res}, 0


def cmd_status(_args):
    branch = _current_branch()
    rc, out, err = _git(["status", "--porcelain"])
    if rc != 0:
        return {"ok": False, "error": "git status failed", **_cmd_result(["git", "status", "--porcelain"], rc, out, err)}, 1

    staged = unstaged = untracked = 0
    for line in out.splitlines():
        if not line:
            continue
        if line.startswith("??"):
            untracked += 1
            continue
        x, y = line[0], line[1]
        if x not in (" ", "?"):
            staged += 1
        if y not in (" ", "?"):
            unstaged += 1

    return {
        "ok": True,
        "branch": branch,
        "staged": staged,
        "unstaged": unstaged,
        "untracked": untracked,
        "dirty": bool(out.strip()),
    }, 0


def cmd_guard_check(args):
    cmd_string = " ".join(args.cmd).strip()
    if not cmd_string:
        return {"ok": False, "blocked": "empty command string"}, 2
    allowed, reason = guard_check(cmd_string, current_branch=_current_branch())
    return {"ok": True, "input": cmd_string, "allowed": allowed, "reason": reason}, 0


def cmd_selftest(_args):
    checks = []

    def chk(name, cond):
        checks.append({"name": name, "pass": bool(cond)})

    a, _ = guard_check("git push --force")
    chk("block force-push", a is False)
    a, _ = guard_check("git reset --hard HEAD~1")
    chk("block reset --hard", a is False)
    a, _ = guard_check("git clean -fdx")
    chk("block clean -fdx", a is False)
    a, _ = guard_check("git commit -m x", current_branch="main")
    chk("block commit on main", a is False)
    a, _ = guard_check("git commit -m x", current_branch="feature/foo")
    chk("allow commit on feature branch", a is True)

    subj, err = build_subject("nope", "core", "message")
    chk("reject bad commit type", subj is None and err is not None)
    subj, err = build_subject("feat", "core", "x" * 80)
    chk("reject >72-char subject", subj is None and err is not None)
    subj, err = build_subject("feat", "api", "add endpoint")
    chk("accept valid subject", subj == "feat(api): add endpoint" and err is None)

    passed = all(c["pass"] for c in checks)
    return {
        "ok": passed,
        "result": "PASS" if passed else "FAIL",
        "checks": checks,
        "total": len(checks),
        "passed": sum(1 for c in checks if c["pass"]),
    }, (0 if passed else 1)


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #
def _human(obj):
    lines = []
    if "blocked" in obj:
        lines.append("BLOCKED: %s" % obj["blocked"])
    if "error" in obj:
        lines.append("ERROR: %s" % obj["error"])
    if "result" in obj:  # selftest
        lines.append(obj["result"])
        for c in obj.get("checks", []):
            lines.append("  [%s] %s" % ("PASS" if c["pass"] else "FAIL", c["name"]))
        lines.append("%d/%d passed" % (obj.get("passed", 0), obj.get("total", 0)))
    for k in ("branch", "dirty", "ahead", "behind", "protected", "created",
              "subject", "head_sha", "head", "base", "draft", "url",
              "staged", "unstaged", "untracked", "allowed", "reason", "input"):
        if k in obj:
            lines.append("%s: %s" % (k, obj[k]))
    if "command" in obj:
        lines.append("$ %s (rc=%s)" % (obj["command"], obj.get("returncode")))
        if obj.get("stderr"):
            lines.append(obj["stderr"])
    if not lines:
        lines.append(json.dumps(obj, ensure_ascii=False))
    return "\n".join(lines)


def emit(obj, as_json, code):
    if as_json:
        print(json.dumps(obj, ensure_ascii=False))
    else:
        print(_human(obj))
    return code


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser():
    parser = argparse.ArgumentParser(
        prog="gitflow.py",
        description="Autonomous Git Guard helper — safe branches, commits, and PRs.",
    )
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="emit one JSON object to stdout")

    sub = parser.add_subparsers(dest="subcommand", required=True)

    sub.add_parser("current", parents=[common], help="show current branch + dirty/ahead/behind")

    p_branch = sub.add_parser("branch", parents=[common], help="create + switch a feature branch")
    p_branch.add_argument("name")

    p_commit = sub.add_parser("commit", parents=[common], help="conventional commit (guarded)")
    p_commit.add_argument("--type", required=True)
    p_commit.add_argument("--scope", required=True)
    p_commit.add_argument("--message", required=True)
    p_commit.add_argument("--body")
    p_commit.add_argument("--all", action="store_true", help="git add -A before committing")

    p_push = sub.add_parser("push", parents=[common], help="push current branch to origin (never force)")
    p_push.add_argument("--set-upstream", action="store_true")

    p_pr = sub.add_parser("pr", parents=[common], help="create a PR via gh")
    p_pr.add_argument("--title", required=True)
    p_pr.add_argument("--body")
    p_pr.add_argument("--base", default="main")
    p_pr.add_argument("--draft", action="store_true")

    sub.add_parser("status", parents=[common], help="porcelain summary")

    p_guard = sub.add_parser("guard-check", parents=[common], help="analyse a git command against deny rules")
    p_guard.add_argument("cmd", nargs="+", help="the proposed git command string")

    sub.add_parser("selftest", parents=[common], help="pure-logic guard checks (no repo mutation)")

    return parser


HANDLERS = {
    "current": cmd_current,
    "branch": cmd_branch,
    "commit": cmd_commit,
    "push": cmd_push,
    "pr": cmd_pr,
    "status": cmd_status,
    "guard-check": cmd_guard_check,
    "selftest": cmd_selftest,
}


def main(argv=None):
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        # argparse already printed usage to stderr; normalise to exit 2
        return 2 if exc.code not in (0, None) else (exc.code or 0)

    handler = HANDLERS.get(args.subcommand)
    if handler is None:  # pragma: no cover - required=True guards this
        parser.print_usage(sys.stderr)
        return 2

    try:
        obj, code = handler(args)
    except Exception as exc:  # never leak a traceback
        return emit({"ok": False, "error": "internal error: %s" % exc}, getattr(args, "json", False), 1)

    return emit(obj, getattr(args, "json", False), code)


if __name__ == "__main__":
    sys.exit(main())
