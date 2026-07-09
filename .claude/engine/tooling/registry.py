#!/usr/bin/env python3
"""SOFI Schema Registry — the Single Source of Truth (SSoT).

Backend agents publish DB schema + API contracts here after a migration;
frontend / mobile agents read the latest to build matching models — no guessing.

State lives under ROOT/.sofi/registry/ :
  db-schema.json      DB tables  -> {version, updated_at, tables{name->{fields[],updated_at}}}
  api-contracts.json  API routes -> {version, updated_at, contracts{key->{method,path,...}}}
  history/<ISO>-<db|api>.json    combined pre-mutation snapshot per mutating op.

Stdlib only. Every subcommand supports --json (one JSON object to stdout).
Exit codes: 0 ok · 1 logical failure (not found / conflict) · 2 usage/misconfig.
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Resolve repo ROOT + state dir identically to sibling tools. SOFI_HOME wins so
# `selftest` (and any caller) can point the whole tool at a throwaway home.
ROOT = Path(os.environ.get("SOFI_HOME") or Path(__file__).resolve().parents[3])
SOFI = ROOT / ".sofi"
# NOTE: mkdir is intentionally lazy (see registry_dir) so `selftest` never
# creates the real ROOT/.sofi — it only spawns children under a temp SOFI_HOME.


class UsageError(Exception):
    """Bad input / misconfiguration -> exit 2."""


class LogicError(Exception):
    """Not found / conflict -> exit 1."""


# --------------------------------------------------------------------------- #
# small helpers
# --------------------------------------------------------------------------- #
def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def safe_ts():
    """Filesystem-safe, lexicographically-sortable timestamp."""
    return now_iso().replace(":", "-")


def registry_dir():
    d = SOFI / "registry"
    d.mkdir(parents=True, exist_ok=True)
    return d


def history_dir():
    d = registry_dir() / "history"
    d.mkdir(parents=True, exist_ok=True)
    return d


def db_path():
    return registry_dir() / "db-schema.json"


def api_path():
    return registry_dir() / "api-contracts.json"


def load_json(path, default):
    if not Path(path).exists():
        return default
    with open(path) as f:
        return json.load(f)


def load_db():
    return load_json(db_path(), {"version": 0, "updated_at": None, "tables": {}})


def load_api():
    return load_json(api_path(), {"version": 0, "updated_at": None, "contracts": {}})


def atomic_write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(obj, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, path)
    except Exception:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def norm(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False)


def _strip(d):
    return {k: v for k, v in d.items() if k != "updated_at"}


def parse_json_arg(raw, label):
    try:
        return json.loads(raw)
    except Exception:
        raise UsageError("%s must be valid JSON" % label)


def validate_fields(raw):
    """--fields must be a JSON array of objects, each with at least name+type."""
    try:
        data = json.loads(raw)
    except Exception:
        raise UsageError("--fields must be valid JSON")
    if not isinstance(data, list):
        raise UsageError("--fields must be a JSON array")
    for f in data:
        if not isinstance(f, dict):
            raise UsageError("each field must be a JSON object")
        if "name" not in f or "type" not in f:
            raise UsageError("each field needs at least 'name' and 'type'")
    return data


def snapshot(kind):
    """Write a combined pre-mutation snapshot of the whole SSoT to history/."""
    hist = history_dir()
    payload = {
        "kind": kind,
        "captured_at": now_iso(),
        "db_schema": load_db(),
        "api_contracts": load_api(),
    }
    while True:  # guarantee a unique, ordered filename
        p = hist / ("%s-%s.json" % (safe_ts(), kind))
        if not p.exists():
            break
    atomic_write(p, payload)
    return p.name


def diff_maps(cur, snap):
    cur_keys, snap_keys = set(cur), set(snap)
    changed = [
        k for k in sorted(cur_keys & snap_keys)
        if norm(_strip(cur[k])) != norm(_strip(snap[k]))
    ]
    return {
        "added": sorted(cur_keys - snap_keys),
        "removed": sorted(snap_keys - cur_keys),
        "changed": changed,
    }


def _emit(result, as_json, human=None):
    if as_json:
        print(json.dumps(result))
    else:
        print(human if human is not None else json.dumps(result, indent=2))


# --------------------------------------------------------------------------- #
# table commands
# --------------------------------------------------------------------------- #
def cmd_set_table(args):
    fields = validate_fields(args.fields)
    db = load_db()
    tables = db.get("tables", {})
    existing = tables.get(args.name)
    if existing is not None and norm(existing.get("fields")) == norm(fields):
        result = {"ok": True, "name": args.name, "changed": False,
                  "db_version": db.get("version", 0)}
        _emit(result, args.json,
              "set-table %s: unchanged (v%d)" % (args.name, db.get("version", 0)))
        return 0
    snapshot("db")
    ts = now_iso()
    tables[args.name] = {"fields": fields, "updated_at": ts}
    db["tables"] = tables
    db["version"] = db.get("version", 0) + 1
    db["updated_at"] = ts
    atomic_write(db_path(), db)
    result = {"ok": True, "name": args.name, "changed": True, "db_version": db["version"]}
    _emit(result, args.json, "set-table %s -> db v%d" % (args.name, db["version"]))
    return 0


def cmd_get_table(args):
    t = load_db().get("tables", {}).get(args.name)
    if t is None:
        raise LogicError("table not found: " + args.name)
    result = {"ok": True, "name": args.name, "table": t}
    _emit(result, args.json, json.dumps(t, indent=2))
    return 0


def cmd_list_tables(args):
    db = load_db()
    tables = [{"name": n, "updated_at": d.get("updated_at")}
              for n, d in sorted(db.get("tables", {}).items())]
    result = {"ok": True, "db_version": db.get("version", 0),
              "count": len(tables), "tables": tables}
    human = "\n".join("%s (%s)" % (t["name"], t["updated_at"]) for t in tables) or "(no tables)"
    _emit(result, args.json, human)
    return 0


def cmd_rm_table(args):
    db = load_db()
    tables = db.get("tables", {})
    if args.name not in tables:
        raise LogicError("table not found: " + args.name)
    snapshot("db")
    ts = now_iso()
    del tables[args.name]
    db["tables"] = tables
    db["version"] = db.get("version", 0) + 1
    db["updated_at"] = ts
    atomic_write(db_path(), db)
    result = {"ok": True, "name": args.name, "removed": True, "db_version": db["version"]}
    _emit(result, args.json, "rm-table %s -> db v%d" % (args.name, db["version"]))
    return 0


# --------------------------------------------------------------------------- #
# contract commands
# --------------------------------------------------------------------------- #
def cmd_set_contract(args):
    api = load_api()
    contracts = api.get("contracts", {})
    new = {"method": args.method.upper(), "path": args.path}
    if args.request is not None:
        new["request"] = parse_json_arg(args.request, "--request")
    if args.response is not None:
        new["response"] = parse_json_arg(args.response, "--response")
    existing = contracts.get(args.key)
    if existing is not None and norm(_strip(existing)) == norm(new):
        result = {"ok": True, "key": args.key, "changed": False,
                  "api_version": api.get("version", 0)}
        _emit(result, args.json,
              "set-contract %s: unchanged (v%d)" % (args.key, api.get("version", 0)))
        return 0
    snapshot("api")
    ts = now_iso()
    entry = dict(new)
    entry["updated_at"] = ts
    contracts[args.key] = entry
    api["contracts"] = contracts
    api["version"] = api.get("version", 0) + 1
    api["updated_at"] = ts
    atomic_write(api_path(), api)
    result = {"ok": True, "key": args.key, "changed": True, "api_version": api["version"]}
    _emit(result, args.json, "set-contract %s -> api v%d" % (args.key, api["version"]))
    return 0


def cmd_get_contract(args):
    c = load_api().get("contracts", {}).get(args.key)
    if c is None:
        raise LogicError("contract not found: " + args.key)
    result = {"ok": True, "key": args.key, "contract": c}
    _emit(result, args.json, json.dumps(c, indent=2))
    return 0


def cmd_list_contracts(args):
    api = load_api()
    contracts = [{"key": k, "method": d.get("method"), "path": d.get("path")}
                 for k, d in sorted(api.get("contracts", {}).items())]
    result = {"ok": True, "api_version": api.get("version", 0),
              "count": len(contracts), "contracts": contracts}
    human = "\n".join("%s  %s %s" % (c["key"], c["method"], c["path"])
                      for c in contracts) or "(no contracts)"
    _emit(result, args.json, human)
    return 0


# --------------------------------------------------------------------------- #
# aggregate commands
# --------------------------------------------------------------------------- #
def cmd_dump(args):
    db, api = load_db(), load_api()
    result = {
        "ok": True,
        "db_version": db.get("version", 0),
        "api_version": api.get("version", 0),
        "tables": db.get("tables", {}),
        "contracts": api.get("contracts", {}),
    }
    _emit(result, args.json,
          "db v%d (%d tables) | api v%d (%d contracts)" % (
              result["db_version"], len(result["tables"]),
              result["api_version"], len(result["contracts"])))
    return 0


def cmd_diff(args):
    snaps = sorted(p for p in history_dir().iterdir() if p.suffix == ".json")
    if not snaps:
        result = {"ok": True, "first": True}
        _emit(result, args.json, "diff: no prior snapshot (first)")
        return 0
    latest = snaps[-1]
    snap = load_json(latest, {})
    snap_db = snap.get("db_schema") or {}
    snap_api = snap.get("api_contracts") or {}
    cur_db, cur_api = load_db(), load_api()
    result = {
        "ok": True,
        "first": False,
        "since": latest.name,
        "tables": diff_maps(cur_db.get("tables", {}), snap_db.get("tables", {})),
        "contracts": diff_maps(cur_api.get("contracts", {}), snap_api.get("contracts", {})),
    }
    _emit(result, args.json, "diff vs %s" % latest.name)
    return 0


# --------------------------------------------------------------------------- #
# selftest — hermetic, runs against a temp SOFI_HOME via subprocess
# --------------------------------------------------------------------------- #
def _rmtree(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for f in files:
            try:
                os.remove(os.path.join(root, f))
            except OSError:
                pass
        for d in dirs:
            try:
                os.rmdir(os.path.join(root, d))
            except OSError:
                pass
    try:
        os.rmdir(path)
    except OSError:
        pass


def cmd_selftest(args):
    tmp = tempfile.mkdtemp(prefix="sofi-registry-selftest-")
    env = dict(os.environ)
    env["SOFI_HOME"] = tmp
    checks = []
    ok = True

    def run(*a):
        p = subprocess.run(
            [sys.executable, os.path.abspath(__file__), *a, "--json"],
            capture_output=True, text=True, env=env)
        try:
            out = json.loads(p.stdout) if p.stdout.strip() else {}
        except Exception:
            out = {"_raw": p.stdout, "_stderr": p.stderr}
        return p.returncode, out

    def check(name, cond):
        checks.append({"check": name, "pass": bool(cond)})
        return bool(cond)

    try:
        rc, r = run("set-table", "users", "--fields",
                    '[{"name":"id","type":"bigint"},'
                    '{"name":"email","type":"varchar","nullable":false}]')
        ok &= check("set-table users rc0", rc == 0)
        ok &= check("users changed", r.get("changed") is True)
        ok &= check("db_version==1", r.get("db_version") == 1)

        rc, r = run("set-table", "orders", "--fields",
                    '[{"name":"id","type":"bigint"},{"name":"total","type":"decimal"}]')
        ok &= check("set-table orders rc0", rc == 0)
        ok &= check("db_version==2", r.get("db_version") == 2)

        rc, r = run("set-table", "orders", "--fields",
                    '[{"name":"id","type":"bigint"},{"name":"total","type":"decimal"}]')
        ok &= check("idempotent: no version bump",
                    r.get("changed") is False and r.get("db_version") == 2)

        rc, r = run("set-contract", "getUser", "--method", "get",
                    "--path", "/api/users/{id}",
                    "--response", '{"id":"int","email":"string"}')
        ok &= check("set-contract rc0", rc == 0)
        ok &= check("api_version==1", r.get("api_version") == 1)

        rc, r = run("dump")
        ok &= check("dump rc0", rc == 0)
        ok &= check("dump db_version==2", r.get("db_version") == 2)
        ok &= check("dump api_version==1", r.get("api_version") == 1)
        ok &= check("dump has 2 tables", len(r.get("tables", {})) == 2)
        ok &= check("dump has 1 contract", len(r.get("contracts", {})) == 1)

        rc, r = run("diff")
        ok &= check("diff rc0", rc == 0)
        ok &= check("diff not first", r.get("first") is False)
        ok &= check("diff added getUser",
                    "getUser" in r.get("contracts", {}).get("added", []))

        rc, r = run("get-table", "users")
        ok &= check("get-table users rc0", rc == 0)

        rc, r = run("get-table", "does-not-exist")
        ok &= check("get-table missing rc1", rc == 1 and r.get("ok") is False)

        rc, r = run("set-table", "bad", "--fields", '{"not":"a-list"}')
        ok &= check("bad --fields rc2", rc == 2 and r.get("ok") is False)
    finally:
        _rmtree(tmp)

    passed = sum(1 for c in checks if c["pass"])
    result = {
        "ok": bool(ok),
        "selftest": "PASS" if ok else "FAIL",
        "passed": passed,
        "total": len(checks),
        "checks": checks,
    }
    _emit(result, args.json,
          "selftest: %s (%d/%d)" % (result["selftest"], passed, len(checks)))
    return 0 if ok else 1


# --------------------------------------------------------------------------- #
# argument parsing
# --------------------------------------------------------------------------- #
def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true",
                        help="emit one JSON object to stdout")

    p = argparse.ArgumentParser(prog="registry",
                                description="SOFI Schema Registry (SSoT).")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("set-table", parents=[common],
                       help="upsert a table (bumps db version + snapshots on change)")
    s.add_argument("name", help="table name")
    s.add_argument("--fields", required=True,
                   help="JSON array of {name,type,nullable?,default?}")
    s.set_defaults(func=cmd_set_table)

    s = sub.add_parser("get-table", parents=[common], help="print one table def")
    s.add_argument("name")
    s.set_defaults(func=cmd_get_table)

    s = sub.add_parser("list-tables", parents=[common],
                       help="list table names + db version")
    s.set_defaults(func=cmd_list_tables)

    s = sub.add_parser("rm-table", parents=[common],
                       help="remove a table (snapshots first)")
    s.add_argument("name")
    s.set_defaults(func=cmd_rm_table)

    s = sub.add_parser("set-contract", parents=[common],
                       help="upsert an API contract (bumps api version + snapshots)")
    s.add_argument("key", help="contract key, e.g. getUser")
    s.add_argument("--method", required=True, help="HTTP method, e.g. GET")
    s.add_argument("--path", required=True, help="route path, e.g. /api/users/{id}")
    s.add_argument("--request", help="optional JSON request shape")
    s.add_argument("--response", help="optional JSON response shape")
    s.set_defaults(func=cmd_set_contract)

    s = sub.add_parser("get-contract", parents=[common], help="print one contract")
    s.add_argument("key")
    s.set_defaults(func=cmd_get_contract)

    s = sub.add_parser("list-contracts", parents=[common],
                       help="list contract keys + method + path")
    s.set_defaults(func=cmd_list_contracts)

    s = sub.add_parser("dump", parents=[common],
                       help="full SSoT (primary read for consumer agents)")
    s.set_defaults(func=cmd_dump)

    s = sub.add_parser("diff", parents=[common],
                       help="compare current SSoT vs most recent snapshot")
    s.set_defaults(func=cmd_diff)

    s = sub.add_parser("selftest", parents=[common],
                       help="run hermetic checks in a temp SOFI_HOME")
    s.set_defaults(func=cmd_selftest)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except UsageError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    except LogicError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 1
    except Exception as e:  # never let a traceback reach the user
        print(json.dumps({"ok": False, "error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
