# Playbook — Cross-Room Dispute Arbitration

> Owner: `brd-arbiter` (feeder: `gtw-conflict-resolver`; escalation ceiling: `brd-ceo`). The Boardroom's sharpest recurring judgment call — a Design-vs-Dev or peer-room deadlock that could not close at the room-Lead level.

## When to run this

A dispute reaches this playbook only after two prior layers have genuinely tried and failed:
1. The two specialists' own room Leads attempted to resolve it directly (same-tier/room negotiation is unrestricted within Article 00's Room Isolation Law).
2. `gtw-conflict-resolver` took the escalated ticket and could not close it either.

A dispute arriving at `brd-arbiter` without both prior attempts documented is **rejected back down** — arbitration is not a shortcut around the room-Lead layer.

## Steps

### 1. Confirm the escalation trail
```bash
sofi brain-query PRJ-XXXX --ticket TKT-NNN --history
```
Read the ticket's full lineage in `HANDOFFS.md`: `escalated_from` chain must show room-Lead attempt → `gtw-conflict-resolver` attempt → now `brd-arbiter`. Missing a link → reject back to `gtw-conflict-resolver` with the specific missing step named.

### 2. Gather both positions' evidence
Read the frozen artifact(s) both sides cite (`file:line` / `§section`), and each side's stated position. No new research is generated here — arbitration rules on evidence already gathered, it doesn't commission new investigation (that would be a room's job, done before the dispute reached this point).

### 3. State the losing position's strongest form (before ruling)
This is deliberate, not optional: write out, in one or two sentences, the strongest honest version of the position about to lose. If it can't be stated well, the ruling isn't ready yet — go back to step 2.

### 4. Apply the doctrine default
- **Design-vs-Dev:** Design wins unless safety or cost forbids it (Teaching I / `company/constitution/01-work-order.md` §6). If overriding the default, name the specific safety or cost constraint that forces it.
- **Peer-room conflict over a shared surface:** the frozen artifact each side cites is the tiebreaker — whichever side's claim matches the actual frozen spec wins; a claim that doesn't match any frozen artifact loses by default (Teaching I: untruth doesn't get a vote).
- **Contested interpretation of an ambiguous frozen artifact:** rules for the interpretation that keeps the artifact internally consistent; if genuinely ambiguous, the artifact itself needs a formal reopen (route back to its owning room via that room's Lead, with the ambiguity named) before the dispute can close.

### 5. Write the ruling — exactly one ADR line
```
ADR-NNN: <date> · gate <N> · by brd-arbiter · <winner> wins <the contested point> because <the specific reason — doctrine default or named override>. Consequence: <what happens next>.
```
File it:
```bash
sofi brain --prj PRJ-XXXX --append DECISIONS.md --entry "ADR-NNN ..."
```

### 6. Close and report
```bash
sofi checkpoint PRJ-XXXX "docs(decisions): ADR-NNN arbitration ruling — <one-line summary>"
```
Report the outcome to `brd-ceo` and to both disputing rooms' Leads directly (Boardroom may address any Lead). Work resumes on the losing side per the ruling — no informal renegotiation.

## Reopening a closed ruling

Only on genuinely new evidence — never on renewed argument from the losing side. A reopen request routes through `gtw-conflict-resolver` first, which confirms the evidence is actually new (not a restatement) before it can return to `brd-arbiter`.

## Rules

- Read-heavy, write-light: one ADR line, one checkpoint, one report. Never a multi-paragraph ruling — if the reasoning needs three paragraphs, the actual ruling hasn't been found.
- Security-substance disputes are never arbitrated here — immediate reroute to `brd-cso`, whose veto sits outside the arbitration chain entirely (Article 07 §1).
- Pairs with `gtw-conflict-resolver`'s escalation intake and `brd-ceo`'s foundation-level backstop (disputes about a Teaching itself, not an application of one, go to the CEO, not the Arbiter).
