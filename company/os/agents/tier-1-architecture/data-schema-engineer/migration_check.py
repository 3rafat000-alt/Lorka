#!/usr/bin/env python3
"""
role:    data-schema-engineer
purpose: enforce "migration without rollback = rejected" — scan migration files
         and fail if any lacks a non-empty down()/rollback path.
gate:    3
inputs:  <path>   a migration file or a directory of them (Laravel/PHP or *.sql)
outputs: a per-file report to stdout
exit:    0 all reversible · 1 one or more irreversible · 2 bad path
"""
import re
import sys
import pathlib

_p = pathlib.Path(__file__).resolve()
for _up in _p.parents:
    if (_up / "sofi_tools").is_dir():
        sys.path.insert(0, str(_up))
        break

_DOWN_PHP = re.compile(r"function\s+down\s*\(\s*\)\s*(?::\s*\w+\s*)?\{(.*?)\}", re.S)
_SQL_DOWN = re.compile(r"--\s*\+migrate\s+Down|^\s*DROP\s+|^\s*ALTER\s+.*\bDROP\b", re.I | re.M)


def _check_php(text: str) -> tuple[bool, str]:
    m = _DOWN_PHP.search(text)
    if not m:
        return False, "no down() method"
    body = m.group(1).strip()
    if not body or body.replace("//", "").strip() == "":
        return False, "down() is empty"
    return True, "down() present"


def _check_sql(text: str) -> tuple[bool, str]:
    if _SQL_DOWN.search(text):
        return True, "down/DROP section present"
    return False, "no reverse (Down/DROP) section"


def check_file(p: pathlib.Path) -> tuple[bool, str]:
    text = p.read_text(encoding="utf-8", errors="replace")
    if p.suffix == ".php":
        return _check_php(text)
    if p.suffix == ".sql":
        return _check_sql(text)
    return True, "skipped (not a migration)"


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: migration_check.py <file-or-dir>", file=sys.stderr)
        return 2
    root = pathlib.Path(argv[0])
    if not root.exists():
        print(f"✗ no such path: {root}", file=sys.stderr)
        return 2
    files = [root] if root.is_file() else sorted(
        [*root.rglob("*.php"), *root.rglob("*.sql")])
    if not files:
        print("(no migration files found)")
        return 0
    bad = 0
    for f in files:
        ok, why = check_file(f)
        mark = "✓" if ok else "✗"
        print(f"  {mark} {f.name}: {why}")
        if not ok:
            bad += 1
    print(f"VERDICT: {'PASS' if not bad else f'REJECT — {bad} irreversible migration(s)'}")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
