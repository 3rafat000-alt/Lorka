"""
tickets — parse and manage the HANDOFFS.md ticket queue.

A ticket is the unit of work passed gate→gate. This module reads the queue,
finds the next open ticket, appends new ones, and closes finished ones — so the
chain stays machine-checkable (every `expected` artifact, every `to:` agent).

Tolerant of both seed formats:
    from: A          |   from: A → to: B
    to:   B          |
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from . import paths, guard

_HEAD = re.compile(r"^##\s*(TKT-\d+)\s*·?\s*gate\s*([0-9\-]+|\d+\s*→\s*gate\s*\d+)", re.I)
_FIELD = re.compile(r"^([a-zA-Z_]+):\s*(.*)$")
_ARROW = re.compile(r"\s*→\s*to:\s*", re.I)

# Tier isolation (engine/protocols/handoff-and-interconnection.md "Tier isolation" section).
# role slug -> tier id ("0".."4"). Advisors are their own bridge role, valid as a
# to:/from: target from any adjacent tier — see ADVISOR_ROLES below.
ROLE_TIER: dict[str, str] = {
    "ceo-sofi": "ceo",
    # Tier 0 — Strategy & Product Design
    "chief-product-strategist": "0", "ux-researcher": "0", "journey-architect": "0",
    "ui-ux-designer": "0", "content-strategist": "0",
    # Tier 1 — System Engineering & Architecture
    "principal-system-architect": "1", "data-schema-engineer": "1",
    "api-integration-specialist": "1", "security-compliance-architect": "1",
    "infrastructure-cloud-architect": "1",
    # Tier 2 — Development Execution
    "database-engineer": "2", "api-engineer": "2", "backend-blade-engineer": "2",
    "frontend-react-engineer": "2", "mobile-engineer": "2",
    # Tier 3 — Quality Assurance & Reliability
    "qa-sre-lead": "3", "automated-testing-engineer": "3", "manual-exploratory-tester": "3",
    "performance-load-analyst": "3", "security-penetration-tester": "3",
    # Tier 4 — Infrastructure & Deployment
    "devops-cloud-lead": "4", "cicd-pipeline-engineer": "4",
    "observability-sre": "4", "release-incident-manager": "4",
}
# role slug -> tier it gates (Advisors are valid to:/from: targets for their own
# tier AND for the two adjacent tiers, since they're the ones who forward across).
ADVISOR_TIER: dict[str, str] = {
    "tier-0-advisor": "0", "tier-1-advisor": "1", "tier-2-advisor": "2",
    "tier-3-advisor": "3", "tier-4-advisor": "4",
}


@dataclass
class Ticket:
    id: str
    gate: str = ""
    frm: str = ""
    to: str = ""
    task: str = ""
    expected: str = ""
    status: str = ""
    extra: dict[str, str] = field(default_factory=dict)

    @property
    def is_open(self) -> bool:
        return self.status.lower().startswith("open")

    @property
    def is_done(self) -> bool:
        return self.status.lower().startswith("done")

    def field(self, name: str) -> str:
        """Return any field by name — canonical (id/gate/from/to/task/expected/status)
        or a v5 structured-brain frontmatter key captured in `extra` (type/mem/date/...)."""
        name = name.lower()
        canon = {"id": self.id, "gate": self.gate, "from": self.frm, "frm": self.frm,
                 "to": self.to, "task": self.task, "expected": self.expected,
                 "status": self.status}
        if name in canon:
            return canon[name]
        return self.extra.get(name, "")


def parse(prj: str) -> list[Ticket]:
    raw = (paths.brain_file(prj, "HANDOFFS").read_text(encoding="utf-8")
           if paths.brain_file(prj, "HANDOFFS").exists() else "")
    tickets: list[Ticket] = []
    cur: Ticket | None = None
    for line in raw.splitlines():
        h = _HEAD.match(line.strip())
        if h:
            cur = Ticket(id=h.group(1), gate=h.group(2).strip())
            tickets.append(cur)
            continue
        if cur is None:
            continue
        m = _FIELD.match(line.strip())
        if not m:
            continue
        key, val = m.group(1).lower(), m.group(2).strip()
        if key == "from" and _ARROW.search(val):
            frm, to = _ARROW.split(val, 1)
            cur.frm, cur.to = frm.strip(), to.strip()
        elif key == "from":
            cur.frm = val
        elif key == "to":
            cur.to = val
        elif key == "task":
            cur.task = val
        elif key == "expected":
            cur.expected = val
        elif key == "status":
            cur.status = val
        else:
            cur.extra[key] = val
    return tickets


def _slugify_ref(ref: str) -> str:
    """A `from:`/`to:` field is free text, often `Tier2.Backend-Blade-Engineer (Aisha)`
    or `@Tier2-Advisor (Elif)` — reduce to the bare role slug for the tier lookup."""
    ref = ref.strip().lstrip("@")
    ref = re.split(r"[·(]", ref, 1)[0].strip()          # drop " (Persona)" / " · note"
    ref = ref.rsplit(".", 1)[-1] if "." in ref else ref  # drop "Tier2." prefix
    return re.sub(r"[\s_]+", "-", ref).strip("-").lower()


def validate_tier_boundary(prj: str) -> list[str]:
    """Tier isolation (handoff-and-interconnection.md "Tier isolation"): a ticket's
    from:/to: may only cross a tier boundary via that tier's Advisor. Returns a list
    of human-readable violation strings (empty = clean). Fails open on any slug this
    module doesn't recognize — free-text ticket fields are common and not every
    variant is worth hard-blocking on.
    """
    violations: list[str] = []
    for t in parse(prj):
        if not t.frm or not t.to:
            continue
        frm_slug, to_slug = _slugify_ref(t.frm), _slugify_ref(t.to)
        if frm_slug in ADVISOR_TIER or to_slug in ADVISOR_TIER:
            continue  # an Advisor on either side is always a valid cross-tier hop
        if frm_slug in ("ceo-sofi",) or to_slug in ("ceo-sofi",):
            continue  # CEO may address anyone
        frm_tier, to_tier = ROLE_TIER.get(frm_slug), ROLE_TIER.get(to_slug)
        if frm_tier is None or to_tier is None:
            continue  # unrecognized slug — don't block on what we can't identify
        if frm_tier != to_tier:
            violations.append(
                f"{t.id}: {t.frm} (tier {frm_tier}) → {t.to} (tier {to_tier}) skips "
                f"both tiers' Advisors — must route via tier-{frm_tier}-advisor "
                f"→ tier-{to_tier}-advisor."
            )
    return violations


def next_open(prj: str) -> Ticket | None:
    for t in parse(prj):
        if t.is_open:
            return t
    return None


def append_ticket(prj: str, *, tkt_id: str, gate: str, frm: str, to: str,
                  task: str, expected: str, route: str = "", status: str = "open") -> None:
    f = paths.brain_file(prj, "HANDOFFS")
    guard.assert_within_project(f, prj)
    block = (
        f"\n## {tkt_id} · gate {gate}\n"
        f"from: {frm} → to: {to}\n"
        f"task: {task}\n"
        f"expected: {expected}\n"
        + (f"route: {route}\n" if route else "")
        + f"status: {status}\n"
    )
    with f.open("a", encoding="utf-8") as fh:
        fh.write(block)


def set_status(prj: str, tkt_id: str, status: str) -> bool:
    """Flip a ticket's status line. Returns True if found+changed."""
    f = paths.brain_file(prj, "HANDOFFS")
    guard.assert_within_project(f, prj)
    lines = f.read_text(encoding="utf-8").splitlines()
    in_block, changed = False, False
    for i, line in enumerate(lines):
        h = _HEAD.match(line.strip())
        if h:
            in_block = (h.group(1) == tkt_id)
            continue
        if in_block and line.strip().lower().startswith("status:"):
            indent = line[: len(line) - len(line.lstrip())]
            lines[i] = f"{indent}status: {status}"
            changed = True
            in_block = False
    if changed:
        f.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changed


def next_id(prj: str) -> str:
    nums = [int(t.id.split("-")[1]) for t in parse(prj) if t.id.split("-")[1].isdigit()]
    return f"TKT-{(max(nums) + 1) if nums else 1:03d}"


def escalate(prj: str, *, tkt_id: str, frm: str, to: str, reason: str,
             gate: str = "", route: str = "") -> str:
    """Escalation chain (The Agency pattern): a blocked agent funnels a decision
    UP the chain instead of rejecting sideways. Files a new up-chain ticket and
    flips the original to 'blocked → escalated'. Returns the new ticket id.

    The new ticket carries `escalated_from:` so the chain is machine-traceable;
    its status is 'open' so it surfaces in the queue / `sofi brain`.
    """
    if not gate:
        # carry the original ticket's gate — _HEAD only parses a numeric gate token,
        # so never emit a non-numeric marker (it would corrupt parsing of this block).
        orig = next((t for t in parse(prj) if t.id == tkt_id), None)
        gate = orig.gate if (orig and orig.gate) else "0"
    new_id = next_id(prj)
    f = paths.brain_file(prj, "HANDOFFS")
    guard.assert_within_project(f, prj)
    block = (
        f"\n## {new_id} · gate {gate}\n"
        f"from: {frm} → to: {to}\n"
        f"task: [ESCALATION from {tkt_id}] {reason}\n"
        f"expected: decision + unblock for {tkt_id}\n"
        + (f"route: {route}\n" if route else "")
        + f"escalated_from: {tkt_id}\n"
        f"status: open\n"
    )
    with f.open("a", encoding="utf-8") as fh:
        fh.write(block)
    set_status(prj, tkt_id, f"blocked → escalated to {to} ({new_id})")
    return new_id


# ── v5 Structured Queryable Brain (C3) ───────────────────────────────────────
def query(prj: str, **filters: str) -> list[Ticket]:
    """Filter the ticket queue by any field — canonical or v5 frontmatter.

    Frontmatter fields (`type`, `mem`, `date`, ...) land in Ticket.extra when a
    ticket block carries them, e.g.:
        ## TKT-021 · gate 4
        from: tier-2-advisor → to: database-engineer
        type: feature
        mem: episodic
        status: open

    Matching is case-insensitive substring on the field value, so
    `query(prj, status="blocked")` catches "blocked → escalated ...". Empty
    filters returns every ticket.
    """
    out = []
    for t in parse(prj):
        if all(v.lower() in t.field(k).lower() for k, v in filters.items()):
            out.append(t)
    return out


# ── v5 Procedural memory: LESSONS.md (C2 reflection engine writes here) ───────
_LESSON_HEAD = re.compile(r"^##\s*(LES-\d+)", re.I)


def next_lesson_id(prj: str) -> str:
    f = paths.brain_file(prj, "LESSONS")
    n = 0
    if f.exists():
        n = len(_LESSON_HEAD.findall(f.read_text(encoding="utf-8")))
    return f"LES-{n + 1:03d}"


def lesson_signatures(prj: str) -> set[str]:
    """The `sig:` line of every existing lesson — the reflection engine uses this
    to avoid writing a duplicate lesson for a pattern it already recorded."""
    f = paths.brain_file(prj, "LESSONS")
    sigs: set[str] = set()
    if not f.exists():
        return sigs
    for line in f.read_text(encoding="utf-8").splitlines():
        m = _FIELD.match(line.strip())
        if m and m.group(1).lower() == "sig":
            sigs.add(m.group(2).strip().lower())
    return sigs


def append_lesson(prj: str, *, situation: str, what_failed: str, rule: str,
                  sig: str, mem: str = "procedural", source: str = "",
                  date: str = "") -> str:
    """Append one distilled lesson (Reflexion-style) to LESSONS.md. `sig` is a
    short dedup signature; `source` cites the ticket/decision it came from (G1).
    Date is supplied by the caller — never invented in a tool."""
    f = paths.brain_file(prj, "LESSONS")
    guard.assert_within_project(f, prj)
    les_id = next_lesson_id(prj)
    block = (
        f"\n## {les_id}"
        + (f" ({date})" if date else "")
        + "\n"
        f"sig: {sig}\n"
        f"mem: {mem}\n"
        f"situation: {situation}\n"
        f"what_failed: {what_failed}\n"
        f"rule: {rule}\n"
        + (f"source: {source}\n" if source else "")
    )
    with f.open("a", encoding="utf-8") as fh:
        fh.write(block)
    return les_id
