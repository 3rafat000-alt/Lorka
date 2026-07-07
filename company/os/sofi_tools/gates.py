"""
gates — the 9-gate lifecycle, in code. Enforce order, forbid skips.

Gate 0 Inception → 1 Discovery → 2 Design → 3 Architecture → 4 Build →
5 Quality → 6 Staging/UAT → 7 Prod → 8 Observe→loop.
"""
from __future__ import annotations

import re

from . import paths, tickets

GATE_ORDER = list(range(0, 9))

GATE_LABEL = {
    0: "Inception", 1: "Discovery", 2: "Solution Design", 3: "Architecture",
    4: "Build", 5: "Quality", 6: "Staging/UAT", 7: "Production", 8: "Observe",
}

# Which roles own each gate (short-names matching routing.yaml).
GATE_ROLES = {
    0: ["chief-product-strategist"],
    1: ["ux-researcher", "journey-architect"],
    2: ["ui-ux-designer", "content-strategist"],
    3: ["principal-system-architect", "data-schema-engineer",
        "api-integration-specialist", "security-compliance-architect"],
    4: ["database-engineer", "api-engineer", "backend-blade-engineer",
        "frontend-react-engineer", "mobile-engineer"],
    5: ["qa-sre-lead", "automated-testing-engineer", "manual-exploratory-tester",
        "performance-load-analyst", "security-penetration-tester"],
    6: ["devops-cloud-lead"],
    7: ["cicd-pipeline-engineer", "devops-cloud-lead"],
    8: ["observability-sre", "release-incident-manager"],
}


def label(gate: int) -> str:
    return GATE_LABEL.get(gate, "?")


def roles_for_gate(gate: int) -> list[str]:
    return GATE_ROLES.get(gate, [])


def _gate_num(raw: str) -> int | None:
    """Pull the first integer out of a gate string like '3' or '8 → gate 1'."""
    for tok in raw.replace("→", " ").split():
        if tok.isdigit():
            return int(tok)
    return None


def validate_no_skip(prj: str) -> dict:
    """Walk the ticket queue forward; confirm gates never skip a step.

    Returns {ok, sequence, skips, loops}. A loop-back (gate N → gate M<N) is
    allowed and reported separately, not counted as a skip.
    """
    seq: list[int] = []
    loops: list[str] = []
    for t in tickets.parse(prj):
        g = _gate_num(t.gate)
        if g is None:
            continue
        if "→" in t.gate:  # explicit loop-back ticket
            loops.append(t.id + ": " + t.gate)
        seq.append(g)

    # forward sequence = monotonic non-decreasing in its first appearance order,
    # never jumping more than +1 between distinct gate levels.
    skips: list[str] = []
    highest = 0
    for g in seq:
        if g > highest + 1:
            skips.append(f"jumped {highest}→{g}")
        highest = max(highest, g)

    return {
        "ok": not skips,
        "sequence": seq,
        "skips": skips,
        "loops": loops,
    }


def validate_tier_boundary(prj: str) -> dict:
    """Every ticket's from:/to: must stay within a tier or cross via that tier's
    Advisor (`sofi_tools.tickets.validate_tier_boundary`). Same PASS/FAIL shape as
    the other two gate validators, so `cmd_gate_check` combines all three uniformly.
    """
    violations = tickets.validate_tier_boundary(prj)
    return {"ok": not violations, "violations": violations}


def validate_artifacts(prj: str) -> dict:
    """Confirm every ticket's `expected: <path>` artifact exists on disk.

    Tickets whose `expected` is a free-text action (no path) are skipped.
    """
    missing, checked = [], []
    base = paths.project_dir(prj)
    for t in tickets.parse(prj):
        exp = t.expected.split()[0] if t.expected else ""
        if exp.startswith(("docs/", "src/")):
            checked.append(exp)
            if not (base / exp).exists():
                missing.append(f"{t.id}: {exp}")
    return {"ok": not missing, "checked": checked, "missing": missing}


# ── v5 Verification: outcome over self-report (verification.md V1, grounding.md G3) ──
# A done-ticket that asserts completion must carry evidence — a run command + its
# output/exit code, a file:line proof, or a git diff/SHA — not just the word "done".
_EVIDENCE = re.compile(
    r"exit[\s_-]?code|exit\s*[:=]?\s*0|passing|passed|\btests?\b.*\b(ran|pass)|"
    r"\.py:\d|\.php:\d|\.dart:\d|:\d+\b|"          # file:line proof
    r"\b[0-9a-f]{7,40}\b|diff|commit|"             # git evidence
    r"```|\$\s",                                    # a pasted command/output block
    re.I,
)


def validate_evidence(prj: str) -> dict:
    """Reject done/passing tickets that assert completion without pasted evidence.

    Same PASS/FAIL shape as the other validators. A ticket is "asserting completion"
    when its status starts with done/passed/complete. Evidence may live in the
    `expected`, `status`, or any `extra` field (e.g. an `evidence:` line). Fail-closed:
    a completion claim with no evidence anywhere in the block is a violation.
    """
    unproven = []
    for t in tickets.parse(prj):
        st = t.status.lower()
        if not st.startswith(("done", "passed", "passing", "complete")):
            continue
        blob = " ".join([t.status, t.expected, t.task, *t.extra.values()])
        if not _EVIDENCE.search(blob):
            unproven.append(
                f"{t.id}: marked '{t.status[:24]}' but carries no evidence "
                f"(paste command+exit code, a file:line proof, or a commit — verification.md V1)."
            )
    return {"ok": not unproven, "unproven": unproven}
