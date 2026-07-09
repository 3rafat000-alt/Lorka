#!/usr/bin/env python3
"""state_db.py — SQLite lifecycle store (the anti-dropped-task guard).

Every task the orchestrator starts is written to a durable SQLite database the
instant it is created and mutated through a *guarded* state machine. Illegal
transitions raise loudly instead of silently corrupting the pipeline, so a task
can never be "dropped" (left in an ambiguous state) or teleport past a stage.

STDLIB ONLY for the store itself. `rich` is used only for pretty selftest
output, with a graceful print-based fallback.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import tempfile
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

# --------------------------------------------------------------------------- #
# Base dir resolution — state always lives under BASE/.sofi/
# --------------------------------------------------------------------------- #
BASE: Path = Path(os.environ.get("SOFI_HOME") or Path(__file__).resolve().parent)
DEFAULT_DB_PATH: Path = BASE / ".sofi" / "orchestrator.db"


# --------------------------------------------------------------------------- #
# rich console with a graceful fallback shim
# --------------------------------------------------------------------------- #
_MARKUP_RE = re.compile(r"\[/?[a-zA-Z0-9 #_.,=-]+\]")


class _ConsoleShim:
    """Minimal stand-in for rich.Console.print when rich is unavailable."""

    @staticmethod
    def print(*args: object, **_kwargs: object) -> None:
        cleaned = [_MARKUP_RE.sub("", str(a)) for a in args]
        print(*cleaned)


try:  # pragma: no cover - exercised implicitly
    from rich.console import Console as _RichConsole

    _console: object = _RichConsole()
except Exception:  # pragma: no cover - fallback path
    _console = _ConsoleShim()


# --------------------------------------------------------------------------- #
# State machine
# --------------------------------------------------------------------------- #
class TaskState(str, Enum):
    """Every stage a task can occupy during its lifecycle."""

    PENDING = "PENDING"
    REFINED = "REFINED"
    BACKEND_PROCESSING = "BACKEND_PROCESSING"
    BACKEND_SUCCESS = "BACKEND_SUCCESS"
    FLUTTER_PROCESSING = "FLUTTER_PROCESSING"
    FLUTTER_SUCCESS = "FLUTTER_SUCCESS"
    QA_VERIFYING = "QA_VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# Linear pipeline; FAILED is reachable from any active (non-terminal) state.
ALLOWED: Dict[TaskState, frozenset] = {
    TaskState.PENDING: frozenset({TaskState.REFINED, TaskState.FAILED}),
    TaskState.REFINED: frozenset(
        {
            TaskState.BACKEND_PROCESSING,
            TaskState.FLUTTER_PROCESSING,
            TaskState.QA_VERIFYING,
            TaskState.FAILED,
        }
    ),
    TaskState.BACKEND_PROCESSING: frozenset(
        {TaskState.BACKEND_SUCCESS, TaskState.FAILED}
    ),
    TaskState.BACKEND_SUCCESS: frozenset(
        {
            TaskState.FLUTTER_PROCESSING,
            TaskState.QA_VERIFYING,
            TaskState.FAILED,
        }
    ),
    TaskState.FLUTTER_PROCESSING: frozenset(
        {TaskState.FLUTTER_SUCCESS, TaskState.FAILED}
    ),
    TaskState.FLUTTER_SUCCESS: frozenset(
        {TaskState.QA_VERIFYING, TaskState.FAILED}
    ),
    TaskState.QA_VERIFYING: frozenset({TaskState.COMPLETED, TaskState.FAILED}),
    TaskState.COMPLETED: frozenset(),  # terminal
    TaskState.FAILED: frozenset(),  # terminal
}


def _now() -> str:
    """UTC ISO-8601 timestamp."""
    return datetime.now(timezone.utc).isoformat()


def _coerce_state(state: object) -> TaskState:
    """Accept a TaskState or its string value; raise ValueError otherwise."""
    if isinstance(state, TaskState):
        return state
    try:
        return TaskState(str(state))
    except ValueError as exc:
        raise ValueError(f"unknown task state: {state!r}") from exc


class StateDB:
    """Durable, transition-guarded task store backed by SQLite (WAL)."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path: Path = Path(db_path) if db_path else DEFAULT_DB_PATH
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise RuntimeError(f"cannot create state dir {self.db_path.parent}: {exc}") from exc
        self._init_db()

    # -- connection helpers ------------------------------------------------- #
    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
        except sqlite3.Error:
            # PRAGMAs are best-effort; a failure here must not crash the store.
            pass
        return conn

    def _init_db(self) -> None:
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        id         INTEGER PRIMARY KEY AUTOINCREMENT,
                        raw_input  TEXT    NOT NULL,
                        payload    TEXT,
                        stack      TEXT,
                        state      TEXT    NOT NULL,
                        error      TEXT,
                        history    TEXT    NOT NULL,
                        created_at TEXT    NOT NULL,
                        updated_at TEXT    NOT NULL
                    );
                    """
                )
        except sqlite3.Error as exc:
            raise RuntimeError(f"cannot initialise state db: {exc}") from exc

    # -- CRUD --------------------------------------------------------------- #
    def create_task(self, raw_input: str) -> int:
        """Insert a new task in PENDING state; return its id."""
        now = _now()
        history = json.dumps([{"state": TaskState.PENDING.value, "at": now}])
        try:
            with self._connect() as conn:
                cur = conn.execute(
                    """
                    INSERT INTO tasks
                        (raw_input, payload, stack, state, error, history, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (raw_input, None, None, TaskState.PENDING.value, None, history, now, now),
                )
                task_id = cur.lastrowid
        except sqlite3.Error as exc:
            raise RuntimeError(f"create_task failed: {exc}") from exc
        if task_id is None:
            raise RuntimeError("create_task failed: no row id returned")
        return int(task_id)

    def set_state(
        self,
        task_id: int,
        state: TaskState,
        *,
        payload: Optional[Dict[str, object]] = None,
        stack: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        """Transition a task to ``state`` (guarded); append to history."""
        target = _coerce_state(state)
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT state, history FROM tasks WHERE id = ?;", (task_id,)
                ).fetchone()
                if row is None:
                    raise ValueError(f"no such task id: {task_id}")

                current = _coerce_state(row["state"])
                allowed = ALLOWED.get(current, frozenset())
                if target not in allowed:
                    raise ValueError(
                        f"illegal transition {current.value} -> {target.value} "
                        f"(allowed: {sorted(s.value for s in allowed) or 'terminal'})"
                    )

                try:
                    history: List[Dict[str, str]] = json.loads(row["history"])
                    if not isinstance(history, list):
                        history = []
                except (json.JSONDecodeError, TypeError):
                    history = []

                now = _now()
                history.append({"state": target.value, "at": now})

                sets = ["state = ?", "history = ?", "updated_at = ?"]
                params: List[object] = [target.value, json.dumps(history), now]
                if payload is not None:
                    sets.append("payload = ?")
                    params.append(json.dumps(payload))
                if stack is not None:
                    sets.append("stack = ?")
                    params.append(stack)
                if error is not None:
                    sets.append("error = ?")
                    params.append(error)
                params.append(task_id)

                conn.execute(
                    f"UPDATE tasks SET {', '.join(sets)} WHERE id = ?;", params
                )
        except sqlite3.Error as exc:
            raise RuntimeError(f"set_state failed: {exc}") from exc

    def get(self, task_id: int) -> Optional[Dict[str, object]]:
        """Return the task as a dict (payload/history parsed) or None."""
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT * FROM tasks WHERE id = ?;", (task_id,)
                ).fetchone()
        except sqlite3.Error as exc:
            raise RuntimeError(f"get failed: {exc}") from exc
        if row is None:
            return None
        return self._row_to_dict(row)

    def list_tasks(self) -> List[Dict[str, object]]:
        """Return all tasks (newest first)."""
        try:
            with self._connect() as conn:
                rows = conn.execute(
                    "SELECT * FROM tasks ORDER BY id DESC;"
                ).fetchall()
        except sqlite3.Error as exc:
            raise RuntimeError(f"list_tasks failed: {exc}") from exc
        return [self._row_to_dict(r) for r in rows]

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, object]:
        def _loads(value: object, default: object) -> object:
            if value in (None, ""):
                return default
            try:
                return json.loads(str(value))
            except (json.JSONDecodeError, TypeError):
                return default

        return {
            "id": row["id"],
            "raw_input": row["raw_input"],
            "payload": _loads(row["payload"], None),
            "stack": row["stack"],
            "state": row["state"],
            "error": row["error"],
            "history": _loads(row["history"], []),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }


# --------------------------------------------------------------------------- #
# Selftest
# --------------------------------------------------------------------------- #
def _selftest() -> bool:
    ok = True
    tmp = tempfile.mkdtemp(prefix="sofi_statedb_")
    os.environ["SOFI_HOME"] = tmp
    db = StateDB(db_path=str(Path(tmp) / ".sofi" / "orchestrator.db"))

    try:
        tid = db.create_task("add phone_number to users table")
        assert isinstance(tid, int) and tid > 0, "create_task must return a positive id"

        task = db.get(tid)
        assert task is not None and task["state"] == TaskState.PENDING.value, "new task must be PENDING"

        db.set_state(tid, TaskState.REFINED, payload={"intent": "demo"}, stack="Both")
        db.set_state(tid, TaskState.BACKEND_PROCESSING)
        db.set_state(tid, TaskState.BACKEND_SUCCESS)
        db.set_state(tid, TaskState.QA_VERIFYING)
        db.set_state(tid, TaskState.COMPLETED)

        task = db.get(tid)
        assert task is not None, "task must exist after transitions"
        assert task["state"] == TaskState.COMPLETED.value, "final state must be COMPLETED"
        # history = PENDING + 5 transitions = 6 entries
        assert len(task["history"]) == 6, f"history len expected 6, got {len(task['history'])}"
        assert task["payload"] == {"intent": "demo"}, "payload must persist"
        assert task["stack"] == "Both", "stack must persist"

        # Illegal jump: COMPLETED is terminal.
        raised = False
        try:
            db.set_state(tid, TaskState.BACKEND_PROCESSING)
        except ValueError:
            raised = True
        assert raised, "illegal transition from terminal state must raise ValueError"

        # Illegal skip on a fresh task: PENDING -> COMPLETED is not allowed.
        tid2 = db.create_task("second task")
        raised2 = False
        try:
            db.set_state(tid2, TaskState.COMPLETED)
        except ValueError:
            raised2 = True
        assert raised2, "PENDING -> COMPLETED skip must raise ValueError"

        # FAILED reachable from an active state.
        db.set_state(tid2, TaskState.REFINED)
        db.set_state(tid2, TaskState.FAILED, error="boom")
        assert db.get(tid2)["state"] == TaskState.FAILED.value, "FAILED must be reachable"

        assert len(db.list_tasks()) == 2, "list_tasks must return both tasks"
    except AssertionError as exc:
        ok = False
        _console.print(f"[red]assertion failed:[/red] {exc}")
    except Exception as exc:  # noqa: BLE001 - selftest guard
        ok = False
        _console.print(f"[red]unexpected error:[/red] {exc}")

    _console.print(f"[bold green]PASS[/bold green] state_db selftest" if ok else "[bold red]FAIL[/bold red] state_db selftest")
    return ok


if __name__ == "__main__":
    import sys

    sys.exit(0 if _selftest() else 1)
