"""
cli — the `sofi` dispatcher every agent calls.

    sofi projects                 list project workspaces
    sofi brain   <PRJ>            show STATE + the next open ticket
    sofi route   <role> [PRIO]    cheapest clearing route (model·effort·caveman)
    sofi gate-check <PRJ>         validate gate order + expected artifacts
    sofi dispatch <PRJ> [role]    render the delegation prompt for the open ticket
    sofi squad <PRJ> <gate>      render parallel delegation for a gate's squad (3·4·5)
    sofi powers                   list the team's superpowers (external_powers)
    sofi handoff <PRJ> close <ID> mark a ticket done
    sofi escalate <PRJ> <ID> <to> "<reason>"  funnel a blocked ticket up-chain
    sofi scratch <PRJ> [clean]    list / purge ephemeral temp scripts
    sofi sync    <PRJ> [--push]   orient: fetch + switch to prj branch + show who did what
    sofi checkpoint <PRJ> "<msg>" commit early/often; auto-appends the SOFI: trailer
    sofi claim   <PRJ> <path>     soft-lock a shared path in LOCKS.md (before editing)
    sofi release <PRJ> <path>     drop a claim
    sofi worktree <PRJ> <gate> <squad>  isolated tree for a parallel squad (gate 3/4/5)
    sofi gate-merge <PRJ> <gate> <squad>  merge a squad's worktree into prj branch at gate close
    sofi gate-tag <PRJ> <gate>    immutable restore point <PRJ>-gate<N>-done
    sofi git-check <PRJ>          verify git hygiene (clean·no leaks·traceable) — gates pipeline
    sofi domain <action> [PRJ]    local domain: init·register·up·down·list·rm·status (e.g. sakk.local)
    sofi tunnel <action> [PRJ]    public tunnel: up·down·list·status (share <slug>.local on the internet)
    sofi tools                    list the registry (shared + per-role scripts)
    sofi doctor                   self-check the library + governance

Exit 0 = ok, non-zero = a gate/governance check failed (CI can gate on it).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import paths, brain, tickets, routing, gates, guard, runlog, gitops, domain, tunnel

_ROUTE_DELEGATION = """\
You are sofi-{role}. Project: {prj}.
BEFORE acting, read in order:
  - engine/protocols/00-operating-system.md   (your contract)
  - engine/protocols/git-discipline.md         (shared-repo rules — read once, obey always)
  - projects/{prj}/_context/STATE.md         (where we are — note branch + head_sha)
  - projects/{prj}/_context/HANDOFFS.md       (your ticket: {tkt})
  - projects/{prj}/_context/CONTEXT.md        (facts so far)
Then ORIENT git — never start blind:
  sofi sync {prj}        # fetch + switch to prj/{prj} + show prior sessions' checkpoints
  git log --oneline -8   # who did what under which ticket (SOFI: trailers)
Before editing a shared path: `sofi claim {prj} <path>` (check LOCKS.md first).
Your spec + Operating Prompt: engine/agents/<path-for-{role}>.md
Your route: {route} (routing.yaml).
Ticket task: {task}
Expected artifact: {expected}
Do the work loop (thinking-and-work.md). Tools per tooling-matrix.md.
CHECKPOINT as you go — never hold >1 artifact uncommitted:
  sofi checkpoint {prj} "<type>(<scope>): <subject>"
AFTER: write artifact, append CONTEXT.md, final `sofi checkpoint {prj} "..."`,
`sofi sync {prj} --push`, record head_sha in STATE.md, write the next ticket in
HANDOFFS.md, mark {tkt} done. An uncommitted session is invisible to the next one.
"""


def _need_project(prj: str) -> None:
    if not paths.project_exists(prj):
        print(f"✗ no such project: {prj} (scaffold with engine/bin/new-project.sh)", file=sys.stderr)
        raise SystemExit(2)


def cmd_projects(_a) -> int:
    pl = paths.list_projects()
    print("\n".join(pl) if pl else "(blank board — no projects)")
    return 0


def cmd_brain(a) -> int:
    _need_project(a.prj)
    st = brain.read_state(a.prj)
    print(f"━━ {a.prj} ━━")
    for k in ("title", "gate", "active", "status", "priority", "blockers", "last_route"):
        if k in st:
            print(f"  {k:10} {st[k]}")
    nxt = tickets.next_open(a.prj)
    if nxt:
        print(f"  next-open  {nxt.id} (gate {nxt.gate}) → {nxt.to}: {nxt.task[:60]}")
    else:
        print("  next-open  (none — queue clear)")
    return 0


def cmd_brain_query(a) -> int:
    """v5 structured-brain query: `sofi brain-query PRJ status=blocked type=feature`.
    Filters the ticket queue by any field (canonical or frontmatter) — case-insensitive
    substring match. Empty filters lists every ticket."""
    _need_project(a.prj)
    filters: dict[str, str] = {}
    for f in a.filters:
        if "=" not in f:
            print(f"  bad filter '{f}' — use key=value"); return 2
        k, v = f.split("=", 1)
        filters[k.strip()] = v.strip()
    rows = tickets.query(a.prj, **filters)
    label = " · ".join(f"{k}={v}" for k, v in filters.items()) or "all"
    print(f"━━ brain-query {a.prj} [{label}] — {len(rows)} match ━━")
    for t in rows:
        extra = " ".join(f"{k}={v}" for k, v in t.extra.items() if k in ("type", "mem"))
        print(f"  {t.id} · gate {t.gate} · {t.status[:24]:24} {extra}  {t.task[:48]}")
    return 0


def cmd_route(a) -> int:
    try:
        r = routing.route_for(a.role, a.priority)
    except KeyError as e:
        print(f"✗ {e}", file=sys.stderr)
        return 2
    print(f"{r['tier']} {r['model']} ({r['model_id']}) · {r['effort']} · {r['caveman']}"
          f"  | gate {r['gate']} | budget {r['budget']} | priority {r['priority']}")
    return 0


def cmd_gate_check(a) -> int:
    _need_project(a.prj)
    order = gates.validate_no_skip(a.prj)
    arts = gates.validate_artifacts(a.prj)
    tier = gates.validate_tier_boundary(a.prj)
    evid = gates.validate_evidence(a.prj)
    print(f"━━ gate-check {a.prj} ━━")
    print(f"  sequence : {' '.join(map(str, order['sequence']))}")
    print(f"  no-skip  : {'✓' if order['ok'] else '✗ ' + '; '.join(order['skips'])}")
    if order["loops"]:
        print(f"  loops    : {', '.join(order['loops'])}")
    print(f"  artifacts: {'✓ all ' + str(len(arts['checked'])) + ' present' if arts['ok'] else '✗ missing ' + '; '.join(arts['missing'])}")
    print(f"  tiers    : {'✓ no boundary violations' if tier['ok'] else '✗ ' + '; '.join(tier['violations'])}")
    print(f"  evidence : {'✓ done-tickets carry proof' if evid['ok'] else '✗ ' + '; '.join(evid['unproven'])}")
    ok = order["ok"] and arts["ok"] and tier["ok"] and evid["ok"]
    print(f"  VERDICT  : {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def cmd_dispatch(a) -> int:
    _need_project(a.prj)
    t = tickets.next_open(a.prj)
    if t is None:
        print("(no open ticket to dispatch)")
        return 0
    role = a.role or t.to
    try:
        route = routing.format_route(role)
    except KeyError:
        route = "(set route per routing.yaml)"
    print(_ROUTE_DELEGATION.format(
        role=role, prj=a.prj, tkt=t.id, route=route,
        task=t.task or "(see ticket)", expected=t.expected or "(see ticket)"))
    return 0


def cmd_handoff(a) -> int:
    _need_project(a.prj)
    if a.op == "close":
        ok = tickets.set_status(a.prj, a.tkt, "done")
    else:
        ok = tickets.set_status(a.prj, a.tkt, a.op)
    print(f"{'✓' if ok else '✗ not found:'} {a.tkt} → {a.op}")
    return 0 if ok else 2


def cmd_escalate(a) -> int:
    _need_project(a.prj)
    tk = next((t for t in tickets.parse(a.prj) if t.id == a.tkt), None)
    if tk is None:
        print(f"✗ no such ticket: {a.tkt}", file=sys.stderr)
        return 2
    nid = tickets.escalate(a.prj, tkt_id=a.tkt, frm=(tk.to or "?"),
                           to=a.to, reason=a.reason, gate=tk.gate)
    print(f"✓ escalated {a.tkt} ({tk.to or '?'}) → {a.to} as {nid}")
    return 0


def cmd_scratch(a) -> int:
    _need_project(a.prj)
    sd = paths.scratch_dir(a.prj)
    sd.mkdir(parents=True, exist_ok=True)
    scripts = sorted(p.name for p in sd.glob("*.py"))
    if a.clean:
        for p in sd.glob("*.py"):
            guard.assert_within_project(p, a.prj)
            p.unlink()
        print(f"✓ purged {len(scripts)} temp script(s) from {a.prj}/_scratch/")
        return 0
    print(f"{a.prj}/_scratch/ — {len(scripts)} temp script(s):")
    for s in scripts:
        print(f"  {s}")
    return 0


def cmd_sync(a) -> int:
    _need_project(a.prj)
    return gitops.sync(a.prj, push=a.push)


def cmd_checkpoint(a) -> int:
    _need_project(a.prj)
    return gitops.checkpoint(a.prj, a.message)


def cmd_claim(a) -> int:
    _need_project(a.prj)
    return gitops.claim(a.prj, a.path)


def cmd_release(a) -> int:
    _need_project(a.prj)
    return gitops.claim(a.prj, a.path, release_it=True)


def cmd_worktree(a) -> int:
    _need_project(a.prj)
    return gitops.worktree(a.prj, str(a.gate), a.squad)


def cmd_gate_merge(a) -> int:
    _need_project(a.prj)
    return gitops.gate_merge(a.prj, str(a.gate), a.squad)


def cmd_gate_tag(a) -> int:
    _need_project(a.prj)
    return gitops.gate_tag(a.prj, str(a.gate))


def cmd_git_check(a) -> int:
    _need_project(a.prj)
    return gitops.git_check(a.prj)


def cmd_domain(a) -> int:
    return domain.run(a.action, getattr(a, "prj", None), getattr(a, "slug", None))


def cmd_tunnel(a) -> int:
    return tunnel.run(a.action, getattr(a, "prj", None), getattr(a, "provider", None))


def cmd_tools(_a) -> int:
    reg = paths.tooling_dir() / "registry.yaml"
    print(reg.read_text(encoding="utf-8") if reg.exists() else "(no registry.yaml)")
    return 0


_SQUADS = {
    "3": ["data-schema-engineer", "api-integration-specialist", "security-compliance-architect"],
    "4": ["database-engineer", "api-engineer", "backend-blade-engineer",
          "frontend-react-engineer", "mobile-engineer"],
    "5": ["automated-testing-engineer", "manual-exploratory-tester",
          "performance-load-analyst", "security-penetration-tester"],
}


def cmd_squad(a) -> int:
    """Render parallel delegation prompts for a gate's squad — agents run concurrently
    behind the frozen upstream input (the parallelism pattern, as a command)."""
    _need_project(a.prj)
    roles = _SQUADS.get(str(a.gate))
    if not roles:
        print(f"✗ no parallel squad for gate {a.gate} (squads: {', '.join(_SQUADS)})", file=sys.stderr)
        return 2
    t = tickets.next_open(a.prj)
    tkt = t.id if t else "(open a ticket in HANDOFFS)"
    print(f"━━ Gate {a.gate} parallel squad — {len(roles)} agents run CONCURRENTLY ━━")
    for role in roles:
        try:
            route = routing.format_route(role)
        except KeyError:
            route = "(set route per routing.yaml)"
        print("\n" + _ROUTE_DELEGATION.format(
            role=role, prj=a.prj, tkt=tkt, route=route,
            task="your slice of this gate — see your ticket in HANDOFFS.md",
            expected="your gate artifact (no skipping)"))
    return 0


def cmd_powers(a) -> int:
    """Surface the team's superpowers (external_powers) from the registry."""
    reg = paths.tooling_dir() / "registry.yaml"
    if not reg.exists():
        print("(no registry.yaml)")
        return 0
    out, grab = [], False
    for ln in reg.read_text(encoding="utf-8").splitlines():
        if ln.startswith("external_powers:"):
            grab = True
        elif grab and ln and not ln[0].isspace() and not ln.lstrip().startswith("#"):
            break
        if grab:
            out.append(ln)
    print("\n".join(out) if out else "(no external_powers — see engine/SUPERPOWERS.md)")
    print("\nfull catalog: engine/SUPERPOWERS.md")
    return 0


def cmd_doctor(_a) -> int:
    import re as _re, glob as _glob, os as _os
    print("━━ sofi doctor ━━")
    ok = True
    root = None
    try:
        root = paths.repo_root()
        print(f"  workspace : {root}")
    except Exception as e:
        print(f"  workspace : ✗ {e}"); ok = False
    try:
        nroutes = len(routing.all_roles())
        print(f"  routing   : ✓ {nroutes} roles")
    except Exception as e:
        print(f"  routing   : ✗ {e}"); ok = False
    print(f"  net-roles : {len(guard.NET_ALLOWED_ROLES)} roles may reach the web")
    print(f"  projects  : {len(paths.list_projects())}")

    # ── agent wiring: subagents ↔ specs (must be equal, both 30) ──────────
    if root:
        subs = _glob.glob(str(root / ".claude/agents/sofi-*.md"))
        specs = _glob.glob(str(root / "engine/agents/**/*.md"), recursive=True)
        if len(subs) == len(specs):
            print(f"  agents    : ✓ {len(subs)} subagents ↔ {len(specs)} specs")
        else:
            print(f"  agents    : ✗ {len(subs)} subagents ≠ {len(specs)} specs"); ok = False

    # ── registry claims: every cited .claude/skills path must exist ───────
    # catches "status: implemented" for a skill whose SKILL.md is missing.
    if root:
        reg = root / "engine/tooling/registry.yaml"
        broken = []
        if reg.exists():
            for m in _re.findall(r'\.claude/skills/[A-Za-z0-9_./-]+', reg.read_text(encoding="utf-8", errors="ignore")):
                if not (root / m).exists():
                    broken.append(m)
        if broken:
            print(f"  skills    : ✗ registry cites {len(broken)} missing path(s): {', '.join(sorted(set(broken)))}"); ok = False
        else:
            print("  skills    : ✓ registry skill paths exist")

    print(f"  VERDICT   : {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def cmd_gemini(a) -> int:
    """External review desk: forward to gemini_review.py (push→receive→parse→act)."""
    import subprocess
    script = paths.tooling_dir() / "agents" / "ceo" / "gemini_review.py"
    if not script.exists():
        print(f"✗ gemini_review.py not found at {script}", file=sys.stderr)
        return 2
    return subprocess.call([sys.executable, str(script), a.op, *a.rest])


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sofi", description="SOFI AI agent tooling dispatcher")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("projects").set_defaults(fn=cmd_projects)

    s = sub.add_parser("brain"); s.add_argument("prj"); s.set_defaults(fn=cmd_brain)

    s = sub.add_parser("brain-query", help="v5: query the ticket queue by field, e.g. status=blocked type=feature")
    s.add_argument("prj"); s.add_argument("filters", nargs="*", default=[])
    s.set_defaults(fn=cmd_brain_query)

    s = sub.add_parser("route"); s.add_argument("role")
    s.add_argument("priority", nargs="?", default=None); s.set_defaults(fn=cmd_route)

    s = sub.add_parser("gate-check"); s.add_argument("prj"); s.set_defaults(fn=cmd_gate_check)

    s = sub.add_parser("dispatch"); s.add_argument("prj")
    s.add_argument("role", nargs="?", default=None); s.set_defaults(fn=cmd_dispatch)

    s = sub.add_parser("squad"); s.add_argument("prj"); s.add_argument("gate")
    s.set_defaults(fn=cmd_squad)

    sub.add_parser("powers").set_defaults(fn=cmd_powers)

    s = sub.add_parser("handoff"); s.add_argument("prj")
    s.add_argument("op"); s.add_argument("tkt"); s.set_defaults(fn=cmd_handoff)

    s = sub.add_parser("escalate"); s.add_argument("prj")
    s.add_argument("tkt"); s.add_argument("to"); s.add_argument("reason")
    s.set_defaults(fn=cmd_escalate)

    s = sub.add_parser("scratch"); s.add_argument("prj")
    s.add_argument("clean", nargs="?", const=True, default=False,
                   help="pass 'clean' to purge temp scripts")
    s.set_defaults(fn=cmd_scratch)

    s = sub.add_parser("sync"); s.add_argument("prj")
    s.add_argument("--push", action="store_true"); s.set_defaults(fn=cmd_sync)

    s = sub.add_parser("checkpoint"); s.add_argument("prj")
    s.add_argument("message"); s.set_defaults(fn=cmd_checkpoint)

    s = sub.add_parser("claim"); s.add_argument("prj")
    s.add_argument("path"); s.set_defaults(fn=cmd_claim)

    s = sub.add_parser("release"); s.add_argument("prj")
    s.add_argument("path"); s.set_defaults(fn=cmd_release)

    s = sub.add_parser("worktree"); s.add_argument("prj")
    s.add_argument("gate"); s.add_argument("squad"); s.set_defaults(fn=cmd_worktree)

    s = sub.add_parser("gate-merge"); s.add_argument("prj")
    s.add_argument("gate"); s.add_argument("squad"); s.set_defaults(fn=cmd_gate_merge)

    s = sub.add_parser("gate-tag"); s.add_argument("prj")
    s.add_argument("gate"); s.set_defaults(fn=cmd_gate_tag)

    s = sub.add_parser("git-check"); s.add_argument("prj"); s.set_defaults(fn=cmd_git_check)

    s = sub.add_parser("domain", help="local domains: init|register|up|down|list|rm|status")
    s.add_argument("action", choices=["init", "register", "up", "down", "list", "rm", "status"])
    s.add_argument("prj", nargs="?", default=None)
    s.add_argument("slug", nargs="?", default=None)
    s.set_defaults(fn=cmd_domain)

    s = sub.add_parser("tunnel", help="public tunnels: up|down|list|status")
    s.add_argument("action", choices=["up", "down", "list", "status"])
    s.add_argument("prj", nargs="?", default=None)
    s.add_argument("provider", nargs="?", default=None,
                   help="cloudflared | localtunnel | auto (default: auto)")
    s.set_defaults(fn=cmd_tunnel)

    s = sub.add_parser("gemini", help="external review desk: review|capture|status (push→receive→act via Gemini)")
    s.add_argument("op", choices=["review", "capture", "status"])
    s.add_argument("rest", nargs=argparse.REMAINDER,
                   help="args passed through to gemini_review.py (e.g. --file --prj --out --ask)")
    s.set_defaults(fn=cmd_gemini)

    sub.add_parser("tools").set_defaults(fn=cmd_tools)
    sub.add_parser("doctor").set_defaults(fn=cmd_doctor)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # normalize 'scratch <prj> clean'
    if getattr(args, "cmd", None) == "scratch" and args.clean == "clean":
        args.clean = True
    try:
        return args.fn(args)
    except guard.GovernanceError as e:
        print(f"✗ GOVERNANCE: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
