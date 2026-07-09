#!/usr/bin/env python3
"""SOFI Task Queue — a deterministic, stateful task queue / state-DB.

A tiny SQLite-backed work queue agents use to hand tasks between each other
with an explicit, enforced state machine:

    pending   -> assigned | cancelled
    assigned  -> running | pending | cancelled   (assign accepts pending|assigned)
    running   -> completed | failed
    failed    -> pending | cancelled
    completed = terminal
    cancelled = terminal   (cancel accepts any non-terminal)

State lives in ROOT/.sofi/tasks.db (SQLite, WAL). Every subcommand supports
--json and emits exactly one JSON object to stdout.

Exit codes: 0 ok · 1 logical failure (illegal transition / not-found) ·
2 usage / bad-JSON. A traceback is never leaked.

Python 3 standard library only.
"""

import argparse
import datetime
import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

# Resolve repo ROOT + state dir. SOFI_HOME wins so `selftest` (and any caller)
# can point the whole tool at a throwaway home.
ROOT = Path(os.environ.get("SOFI_HOME") or Path(__file__).resolve().parents[3])
SOFI = ROOT / ".sofi"
DB = SOFI / "tasks.db"
# NOTE: ROOT/.sofi is created lazily inside connect() — NOT at import time — so
# that `selftest` (which redirects SOFI/DB to a throwaway temp dir) never
# creates or touches the real ROOT/.sofi merely by importing this module.

# --------------------------------------------------------------------------- #
# state machine
# --------------------------------------------------------------------------- #
TERMINAL = {"completed", "cancelled"}
STATUSES = ["pending", "assigned", "running", "completed", "failed", "cancelled"]
NON_TERMINAL = [s for s in STATUSES if s not in TERMINAL]


class UsageError(Exception):
    """Bad input / bad JSON -> exit 2."""


class LogicError(Exception):
    """Illegal transition / not-found -> exit 1."""


# --------------------------------------------------------------------------- #
# small helpers
# --------------------------------------------------------------------------- #
def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def connect():
    """Open the DB, creating ROOT/.sofi + the table on demand. WAL journaling."""
    SOFI.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS agent_tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id   INTEGER,
            assigned_to TEXT,
            action      TEXT NOT NULL,
            status      TEXT NOT NULL,
            payload     TEXT,
            result      TEXT,
            error       TEXT,
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        )"""
    )
    conn.commit()
    return conn


def row_to_dict(row):
    return {k: row[k] for k in row.keys()}


def fetch(conn, task_id):
    row = conn.execute(
        "SELECT * FROM agent_tasks WHERE id = ?", (task_id,)
    ).fetchone()
    if row is None:
        raise LogicError("task %s not found" % task_id)
    return row_to_dict(row)


def guard(current, allowed_sources, verb):
    """Reject an illegal transition with a clear message (-> exit 1)."""
    if current not in allowed_sources:
        raise LogicError(
            "illegal transition: cannot %s a '%s' task (allowed from: %s)"
            % (verb, current, ", ".join(allowed_sources))
        )


def parse_json_arg(name, raw):
    """Validate that --payload/--result is JSON; raise UsageError (-> exit 2)."""
    if raw is None:
        return None
    try:
        json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise UsageError("--%s is not valid JSON: %s" % (name, exc))
    return raw  # stored verbatim (the column is TEXT)


def _update(conn, task_id, **cols):
    """Parametrised UPDATE; keys are code-controlled column names only."""
    cols["updated_at"] = now_iso()
    assignments = ", ".join("%s = ?" % k for k in cols)
    params = list(cols.values()) + [task_id]
    conn.execute(
        "UPDATE agent_tasks SET %s WHERE id = ?" % assignments, params
    )
    conn.commit()


# --------------------------------------------------------------------------- #
# subcommands
# --------------------------------------------------------------------------- #
def cmd_create(conn, args):
    parse_json_arg("payload", args.payload)
    ts = now_iso()
    cur = conn.execute(
        "INSERT INTO agent_tasks "
        "(parent_id, assigned_to, action, status, payload, result, error, "
        " created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (args.parent, args.to, args.action, "pending", args.payload,
         None, None, ts, ts),
    )
    conn.commit()
    task_id = cur.lastrowid
    row = fetch(conn, task_id)
    # Dual key: consumers may read either "id" or "task_id" (same integer).
    row["task_id"] = task_id
    return row


def cmd_assign(conn, args):
    row = fetch(conn, args.id)
    guard(row["status"], ("pending", "assigned"), "assign")
    _update(conn, args.id, status="assigned", assigned_to=args.to)
    return fetch(conn, args.id)


def cmd_start(conn, args):
    row = fetch(conn, args.id)
    guard(row["status"], ("assigned",), "start")
    _update(conn, args.id, status="running")
    return fetch(conn, args.id)


def cmd_done(conn, args):
    parse_json_arg("result", args.result)
    row = fetch(conn, args.id)
    guard(row["status"], ("running",), "complete")
    _update(conn, args.id, status="completed", result=args.result)
    return fetch(conn, args.id)


def cmd_fail(conn, args):
    row = fetch(conn, args.id)
    guard(row["status"], ("running",), "fail")
    _update(conn, args.id, status="failed", error=args.error)
    return fetch(conn, args.id)


def cmd_retry(conn, args):
    row = fetch(conn, args.id)
    guard(row["status"], ("failed",), "retry")
    _update(conn, args.id, status="pending", assigned_to=None, error=None)
    return fetch(conn, args.id)


def cmd_cancel(conn, args):
    row = fetch(conn, args.id)
    guard(row["status"], tuple(NON_TERMINAL), "cancel")
    _update(conn, args.id, status="cancelled")
    return fetch(conn, args.id)


def cmd_show(conn, args):
    return fetch(conn, args.id)


def cmd_list(conn, args):
    sql = "SELECT * FROM agent_tasks"
    where, params = [], []
    if args.status:
        where.append("status = ?")
        params.append(args.status)
    if args.to:
        where.append("assigned_to = ?")
        params.append(args.to)
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id DESC"  # newest first
    if args.limit is not None:
        sql += " LIMIT ?"
        params.append(args.limit)
    rows = [row_to_dict(r) for r in conn.execute(sql, params).fetchall()]
    return {"tasks": rows, "count": len(rows)}


def cmd_next(conn, args):
    sql = "SELECT * FROM agent_tasks WHERE status = 'pending'"
    params = []
    if args.to:
        sql += " AND assigned_to = ?"
        params.append(args.to)
    sql += " ORDER BY id ASC LIMIT 1"  # oldest pending
    row = conn.execute(sql, params).fetchone()
    return row_to_dict(row) if row is not None else {}


def cmd_orphans(conn, args):
    threshold = args.older_than
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        seconds=threshold
    )
    cutoff_iso = cutoff.isoformat()
    rows = conn.execute(
        "SELECT * FROM agent_tasks "
        "WHERE status IN ('pending', 'assigned') AND created_at < ? "
        "ORDER BY created_at ASC",
        (cutoff_iso,),
    ).fetchall()
    tasks = [row_to_dict(r) for r in rows]
    return {"tasks": tasks, "count": len(tasks), "older_than": threshold}


def cmd_stats(conn, args):
    rows = conn.execute(
        "SELECT status, COUNT(*) AS c FROM agent_tasks GROUP BY status"
    ).fetchall()
    counts = {s: 0 for s in STATUSES}
    for r in rows:
        counts[r["status"]] = r["c"]
    return {"counts": counts, "total": sum(counts.values())}


DISPATCH = {
    "create": cmd_create,
    "assign": cmd_assign,
    "start": cmd_start,
    "done": cmd_done,
    "fail": cmd_fail,
    "retry": cmd_retry,
    "cancel": cmd_cancel,
    "show": cmd_show,
    "list": cmd_list,
    "next": cmd_next,
    "orphans": cmd_orphans,
    "stats": cmd_stats,
}


# --------------------------------------------------------------------------- #
# selftest — runs against a throwaway SOFI_HOME, never touches real ROOT/.sofi
# --------------------------------------------------------------------------- #
def _ns(**kw):
    return argparse.Namespace(**kw)


def _rmtree(path):
    """Best-effort recursive delete (shutil not used)."""
    p = Path(path)
    if not p.exists():
        return
    for child in sorted(p.rglob("*"), key=lambda x: len(x.parts), reverse=True):
        try:
            if child.is_dir() and not child.is_symlink():
                child.rmdir()
            else:
                child.unlink()
        except OSError:
            pass
    try:
        p.rmdir()
    except OSError:
        pass


def cmd_selftest(args):
    global SOFI, DB
    tmp = Path(tempfile.mkdtemp(prefix="taskq-selftest-"))
    saved = (SOFI, DB)
    SOFI = tmp / ".sofi"
    DB = SOFI / "tasks.db"
    ok, detail = True, []
    try:
        conn = connect()
        # 1. create -> assign -> start -> done
        t1 = cmd_create(conn, _ns(action="SELFTEST_1", to=None,
                                  payload='{"k":1}', parent=None))
        assert t1["status"] == "pending", "new task must be pending"
        assert t1["id"] == t1["task_id"], "id and task_id must match"
        cmd_assign(conn, _ns(id=t1["id"], to="agent-a"))
        cmd_start(conn, _ns(id=t1["id"]))
        d1 = cmd_done(conn, _ns(id=t1["id"], result='{"ok":true}'))
        assert d1["status"] == "completed", "task must reach completed"

        # 2. create + assign a 2nd; it must surface in orphans --older-than 0
        t2 = cmd_create(conn, _ns(action="SELFTEST_2", to="agent-b",
                                  payload=None, parent=None))
        cmd_assign(conn, _ns(id=t2["id"], to="agent-b"))
        orph = cmd_orphans(conn, _ns(older_than=0))
        assert any(x["id"] == t2["id"] for x in orph["tasks"]), \
            "assigned task must appear in orphans --older-than 0"

        # 3. illegal transition: done on a pending -> must be rejected (exit 1)
        t3 = cmd_create(conn, _ns(action="SELFTEST_3", to=None,
                                  payload=None, parent=None))
        rejected = False
        try:
            cmd_done(conn, _ns(id=t3["id"], result=None))
        except LogicError:
            rejected = True
        assert rejected, "illegal transition (done on pending) not rejected"

        conn.close()
    except AssertionError as exc:
        ok = False
        detail.append(str(exc))
    except Exception as exc:  # never leak a traceback
        ok = False
        detail.append("%s: %s" % (type(exc).__name__, exc))
    finally:
        SOFI, DB = saved
        _rmtree(tmp)

    out = {"ok": ok, "selftest": "PASS" if ok else "FAIL"}
    if detail:
        out["detail"] = detail
    return out, (0 if ok else 1)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true",
                        help="emit one JSON object to stdout")

    parser = argparse.ArgumentParser(
        prog="taskq", parents=[common],
        description="SOFI stateful task queue (SQLite state-DB).",
    )
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("create", parents=[common])
    p.add_argument("--action", required=True)
    p.add_argument("--to")
    p.add_argument("--payload")
    p.add_argument("--parent", type=int)

    p = sub.add_parser("assign", parents=[common])
    p.add_argument("id", type=int)
    p.add_argument("--to", required=True)

    for name in ("start", "retry", "cancel", "show"):
        p = sub.add_parser(name, parents=[common])
        p.add_argument("id", type=int)

    p = sub.add_parser("done", parents=[common])
    p.add_argument("id", type=int)
    p.add_argument("--result")

    p = sub.add_parser("fail", parents=[common])
    p.add_argument("id", type=int)
    p.add_argument("--error")

    p = sub.add_parser("list", parents=[common])
    p.add_argument("--status")
    p.add_argument("--to")
    p.add_argument("--limit", type=int)

    p = sub.add_parser("next", parents=[common])
    p.add_argument("--to")

    p = sub.add_parser("orphans", parents=[common])
    p.add_argument("--older-than", type=int, default=900, dest="older_than")

    sub.add_parser("stats", parents=[common])
    sub.add_parser("selftest", parents=[common])

    return parser


def emit(obj, as_json):
    if as_json:
        sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    else:
        sys.stdout.write(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    parser = build_parser()
    args = parser.parse_args(argv)
    as_json = getattr(args, "json", False)

    if args.command is None:
        parser.error("a subcommand is required")  # prints usage, exits 2

    # selftest owns its own throwaway DB — never open the real one for it.
    if args.command == "selftest":
        obj, code = cmd_selftest(args)
        emit(obj, as_json)
        return code

    try:
        conn = connect()
        try:
            obj = DISPATCH[args.command](conn, args)
        finally:
            conn.close()
        emit(obj, as_json)
        return 0
    except UsageError as exc:
        emit({"ok": False, "error": str(exc)}, as_json)
        return 2
    except LogicError as exc:
        emit({"ok": False, "error": str(exc)}, as_json)
        return 1
    except Exception as exc:  # never leak a traceback
        emit({"ok": False, "error": "%s: %s" % (type(exc).__name__, exc)},
             as_json)
        return 2


if __name__ == "__main__":
    sys.exit(main())
