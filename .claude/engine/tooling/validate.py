#!/usr/bin/env python3
"""SOFI Maestro Guard — payload validator.

Rejects malformed delegation / gateway payloads BEFORE they reach an executor
agent. Implements a MINIMAL, self-contained JSON-Schema (draft-07 subset)
validator so the enterprise never has to install `jsonschema`.

Supported keywords:
  type (string OR list; object/array/string/number/integer/boolean/null),
  required, properties, additionalProperties (bool), items, enum, minLength,
  minItems, pattern (re), const.

Design notes:
  * ALL errors are collected, not just the first — shape is
    [{"path": "actions[0].sub_system", "message": ".."}].
  * `bool` NEVER satisfies `integer` or `number` (Python treats bool as int;
    we exclude it explicitly).
  * Every subcommand accepts --json and emits exactly ONE JSON object to stdout.

Exit codes:
  0  VALID / PASS
  1  INVALID / REJECT (with reasons)
  2  usage / misconfig (bad JSON, missing payload, unreadable schema, ...)

Stdlib only (json, argparse, os, sys, pathlib, re). No third-party imports.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# --- Roots -----------------------------------------------------------------
ROOT = Path(os.environ.get("SOFI_HOME") or Path(__file__).resolve().parents[3])
SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"

BUILTIN = {
    "delegation": SCHEMA_DIR / "delegation.schema.json",
    "gateway": SCHEMA_DIR / "gateway.schema.json",
}

KNOWN_TYPES = {"object", "array", "string", "number", "integer", "boolean", "null"}


# --- Minimal JSON-Schema validator -----------------------------------------
def _typename(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _matches_type(value, t):
    """True if `value` satisfies the single JSON-Schema type name `t`."""
    if t == "object":
        return isinstance(value, dict)
    if t == "array":
        return isinstance(value, list)
    if t == "string":
        return isinstance(value, str)
    if t == "boolean":
        return isinstance(value, bool)
    if t == "null":
        return value is None
    if t == "integer":
        # bool is a subclass of int -> exclude it explicitly.
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    # Unknown type keyword -> impose no constraint.
    return True


def _join(path, key):
    return str(key) if not path else "{}.{}".format(path, key)


def _index(path, i):
    return "{}[{}]".format(path, i)


def _err(errors, path, message):
    errors.append({"path": path or "<root>", "message": message})


def validate(instance, schema, path, errors):
    """Validate `instance` against `schema`, appending every error found."""
    # Boolean schemas (draft-07): True accepts anything, False accepts nothing.
    if schema is True:
        return
    if schema is False:
        _err(errors, path, "schema is false; no value is allowed here")
        return
    if not isinstance(schema, dict):
        return  # malformed subschema -> nothing to assert

    # type (must pass before deeper keywords are meaningful)
    if "type" in schema:
        types = schema["type"]
        if isinstance(types, str):
            types = [types]
        if isinstance(types, list):
            if not any(_matches_type(instance, t) for t in types):
                _err(errors, path, "expected type {}, got {}".format(
                    "|".join(str(t) for t in types), _typename(instance)))
                return  # further checks would be spurious against wrong type

    # const
    if "const" in schema and instance != schema["const"]:
        _err(errors, path, "value {!r} does not equal const {!r}".format(
            instance, schema["const"]))

    # enum
    if "enum" in schema and instance not in schema["enum"]:
        _err(errors, path, "value {!r} is not in enum {}".format(
            instance, schema["enum"]))

    # string constraints
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            _err(errors, path, "string length {} is below minLength {}".format(
                len(instance), schema["minLength"]))
        if "pattern" in schema:
            try:
                if re.search(schema["pattern"], instance) is None:
                    _err(errors, path, "string does not match pattern {!r}".format(
                        schema["pattern"]))
            except re.error as exc:
                _err(errors, path, "invalid pattern in schema: {}".format(exc))

    # array constraints
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            _err(errors, path, "array length {} is below minItems {}".format(
                len(instance), schema["minItems"]))
        items = schema.get("items")
        if isinstance(items, (dict, bool)):
            for i, item in enumerate(instance):
                validate(item, items, _index(path, i), errors)

    # object constraints
    if isinstance(instance, dict):
        props = schema.get("properties", {})
        if isinstance(props, dict):
            required = schema.get("required", [])
            if isinstance(required, list):
                for key in required:
                    if key not in instance:
                        _err(errors, _join(path, key),
                             "required property '{}' is missing".format(key))
            for key, subschema in props.items():
                if key in instance:
                    validate(instance[key], subschema, _join(path, key), errors)
            if schema.get("additionalProperties", True) is False:
                for key in instance:
                    if key not in props:
                        _err(errors, _join(path, key),
                             "additional property '{}' is not allowed".format(key))


# --- Loading ---------------------------------------------------------------
def load_payload(args):
    """Return (data, error). error is None on success."""
    payload_file = getattr(args, "payload_file", None)
    if payload_file:
        p = Path(payload_file)
        if not p.exists():
            return None, "payload file not found: {}".format(payload_file)
        try:
            raw = p.read_text()
        except OSError as exc:
            return None, "cannot read payload file: {}".format(exc)
    elif getattr(args, "payload", None) is not None:
        raw = args.payload
    else:
        return None, "no payload provided (use --payload or --payload-file)"
    try:
        return json.loads(raw), None
    except ValueError as exc:
        return None, "invalid JSON: {}".format(exc)


def load_schema(path):
    """Return (schema_dict, error). error is None on success."""
    p = Path(path)
    if not p.exists():
        return None, "schema file not found: {}".format(path)
    try:
        raw = p.read_text()
    except OSError as exc:
        return None, "cannot read schema file: {}".format(exc)
    try:
        data = json.loads(raw)
    except ValueError as exc:
        return None, "invalid schema JSON: {}".format(exc)
    if not isinstance(data, dict):
        return None, "schema root is not a JSON object"
    return data, None


# --- Output ----------------------------------------------------------------
def human(obj):
    if "selftest" in obj:
        lines = []
        for c in obj.get("cases", []):
            mark = "PASS" if c["pass"] else "FAIL"
            suffix = "" if c["pass"] else "  -- " + c.get("detail", "")
            lines.append("[{}] {}{}".format(mark, c["name"], suffix))
        lines.append("selftest: " + obj["selftest"])
        return "\n".join(lines)
    if isinstance(obj.get("schemas"), list):
        lines = ["root:       {}".format(obj.get("root", ""))]
        lines.append("schema dir: {}".format(obj.get("dir", "")))
        for s in obj["schemas"]:
            lines.append("  {:12s} {}  (exists={})".format(
                s["name"], s["path"], s["exists"]))
        return "\n".join(lines)
    if obj.get("ok") is True and "schema" in obj:
        return "VALID    schema={}".format(obj["schema"])
    if obj.get("ok") is False and "errors" in obj:
        errs = obj["errors"]
        lines = ["INVALID  schema={}  ({} error{})".format(
            obj.get("schema", "?"), len(errs), "" if len(errs) == 1 else "s")]
        for e in errs:
            lines.append("  {}: {}".format(e["path"], e["message"]))
        return "\n".join(lines)
    if obj.get("ok") is False and "error" in obj:
        return "ERROR: {}".format(obj["error"])
    return json.dumps(obj)


def emit(obj, args):
    if getattr(args, "json", False):
        print(json.dumps(obj, indent=2))
    else:
        print(human(obj))


def fail_usage(message, args, **extra):
    obj = {"ok": False, "error": message}
    obj.update(extra)
    emit(obj, args)
    return 2


def do_validate(instance, schema, name, args):
    errors = []
    validate(instance, schema, "", errors)
    if errors:
        emit({"ok": False, "schema": name, "errors": errors}, args)
        return 1
    emit({"ok": True, "schema": name}, args)
    return 0


# --- Subcommands -----------------------------------------------------------
def _run_builtin(name, args):
    instance, perr = load_payload(args)
    if perr:
        return fail_usage(perr, args, schema=name)
    schema, serr = load_schema(BUILTIN[name])
    if serr:
        return fail_usage(serr, args, schema=name)
    return do_validate(instance, schema, name, args)


def cmd_delegation(args):
    return _run_builtin("delegation", args)


def cmd_gateway(args):
    return _run_builtin("gateway", args)


def cmd_against(args):
    schema, serr = load_schema(args.schema)
    if serr:
        return fail_usage(serr, args)
    instance, perr = load_payload(args)
    if perr:
        return fail_usage(perr, args)
    return do_validate(instance, schema, Path(args.schema).name, args)


def cmd_schemas(args):
    items = []
    for name, path in BUILTIN.items():
        items.append({"name": name, "path": str(path), "exists": Path(path).exists()})
    emit({"ok": True, "root": str(ROOT), "dir": str(SCHEMA_DIR), "schemas": items}, args)
    return 0


def _errors_for(name, payload):
    """Validate `payload` against a built-in schema; return (errors, load_error)."""
    schema, serr = load_schema(BUILTIN[name])
    if serr:
        return None, serr
    errors = []
    validate(payload, schema, "", errors)
    return errors, None


def cmd_selftest(args):
    cases = []

    def record(name, condition, detail):
        cases.append({"name": name, "pass": bool(condition), "detail": detail})

    # (a) valid delegation -> PASS (zero errors)
    valid_del = {"sender": "brd-ceo", "recipient": "bck-api-engineer",
                 "action": "MODIFY_ENDPOINT", "parameters": {"endpoint": "/x"},
                 "task_id": 7}
    errs, serr = _errors_for("delegation", valid_del)
    if serr:
        record("valid delegation PASS", False, serr)
    else:
        record("valid delegation PASS", len(errs) == 0, "errors={}".format(errs))

    # (b) delegation missing 'recipient' + bad 'action' -> REJECT listing BOTH
    bad_del = {"sender": "brd-ceo", "action": "NOT_A_REAL_ACTION", "parameters": {}}
    errs, serr = _errors_for("delegation", bad_del)
    if serr:
        record("delegation missing recipient + bad action -> REJECT both", False, serr)
    else:
        paths = [e["path"] for e in errs]
        both = ("recipient" in paths) and ("action" in paths)
        record("delegation missing recipient + bad action -> REJECT both",
               both and len(errs) >= 2, "paths={}".format(paths))

    # (c) valid gateway -> PASS
    valid_gw = {"instruction_type": "FEATURE_EXPANSION",
                "target_stacks": ["Laravel_v12"],
                "actions": [{"sub_system": "BACKEND", "task": "add endpoint"}]}
    errs, serr = _errors_for("gateway", valid_gw)
    if serr:
        record("valid gateway PASS", False, serr)
    else:
        record("valid gateway PASS", len(errs) == 0, "errors={}".format(errs))

    # (d) gateway actions=[] -> REJECT (minItems)
    empty_gw = {"instruction_type": "BUG_FIX",
                "target_stacks": ["Laravel_v12"], "actions": []}
    errs, serr = _errors_for("gateway", empty_gw)
    if serr:
        record("gateway actions=[] -> REJECT (minItems)", False, serr)
    else:
        hit = any(e["path"] == "actions" and "minItems" in e["message"] for e in errs)
        record("gateway actions=[] -> REJECT (minItems)",
               hit and len(errs) >= 1, "errors={}".format(errs))

    all_pass = all(c["pass"] for c in cases)
    emit({"ok": all_pass, "selftest": "PASS" if all_pass else "FAIL",
          "cases": cases}, args)
    return 0 if all_pass else 1


# --- CLI -------------------------------------------------------------------
def build_parser():
    parser = argparse.ArgumentParser(
        prog="validate",
        description="SOFI Maestro guard — validate delegation/gateway payloads")

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true",
                        help="emit exactly one JSON object to stdout")

    payload = argparse.ArgumentParser(add_help=False)
    payload.add_argument("--payload", default=None, help="inline JSON payload string")
    payload.add_argument("--payload-file", dest="payload_file", default=None,
                         help="path to a JSON payload file")

    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("delegation", parents=[common, payload],
                   help="validate a payload against the delegation schema")
    sub.add_parser("gateway", parents=[common, payload],
                   help="validate a payload against the gateway schema")
    ag = sub.add_parser("against", parents=[common, payload],
                        help="validate a payload against an arbitrary schema file")
    ag.add_argument("--schema", required=True, help="path to a JSON Schema file")
    sub.add_parser("schemas", parents=[common],
                   help="list the built-in schemas and their paths")
    sub.add_parser("selftest", parents=[common],
                   help="self-test the validator (no dependency on ROOT/.sofi)")
    return parser


DISPATCH = {
    "delegation": cmd_delegation,
    "gateway": cmd_gateway,
    "against": cmd_against,
    "schemas": cmd_schemas,
    "selftest": cmd_selftest,
}


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return DISPATCH[args.command](args)
    except SystemExit:
        raise
    except Exception as exc:  # never leak a traceback
        payload = {"ok": False, "error": "{}: {}".format(type(exc).__name__, exc)}
        if getattr(args, "json", False):
            print(json.dumps(payload, indent=2))
        else:
            sys.stderr.write("error: {}: {}\n".format(type(exc).__name__, exc))
        return 2


if __name__ == "__main__":
    sys.exit(main())
