# Routing Policy — Effort-Based Task Routing

## Core Principle

**Cheapest route that clears bar.** Every task gets minimum viable effort. Waste = defect.

> Model is unified (`opencode/big-pickle`). Routing is effort-based, not model-based.

## Routing Ladder (escalate on evidence)

| Tier | Tag | Effort | When |
|------|-----|--------|------|
| 🟢 Mechanical | 1× | 80% of tasks — boilerplate, grep, format, git ops, simple edits, single-file changes |
| 🔵 Workhorse | 3× | Clear coding — controllers, Blade views, migrations, tests, reviews |
| 🔮 Gatekeeper | 10× | Cross-layer sweeps — full-stack features, spec reviews, architecture arbitration |
| 🟣 Deep | 20× | Last resort — repo-wide deep debugging, unknown-source total failures |

**Rules:**
- Start at mechanical. Escalate only when blocked.
- Evidence required for escalation: "mechanical failed because X"
- Deep is FORBIDDEN for routine code-writing
- Log every escalation with reason

## Effort Scaling

| Class | Max Calls | Max Agents (parallel) | Fail-Safe |
|-------|-----------|----------------------|-----------|
| trivial-fix | 3 | 1 | 3 attempts -> escalate |
| single-role | 10 | 1 | 3 attempts -> escalate |
| cross-tier | 30 | 3 | 3 attempts -> escalate |
| audit-sweep | 50 | 5 | 3 attempts -> escalate |
| arbitration | 10 | 1 (deep) | 1 attempt -> escalate |

## Effort Class Selection

| Task Type | Default Class |
|-----------|--------------|
| Typo fix, rename, label change | trivial-fix |
| Single endpoint, one Blade view, one migration | single-role |
| Feature across backend + frontend | cross-tier |
| Full security audit, migration consolidation | audit-sweep |
| Design-vs-engineering conflict, cross-room deadlock | arbitration |

## Anti-Patterns

| Anti-Pattern | Why |
|--------------|-----|
| Deep for CRUD form ❌ | Waste — mechanical/workhorse does it |
| Mechanical for threat model ❌ | Too complex — needs gatekeeper |
| No route logged ❌ | Untracked cost |
| Caveman off for routine chat ❌ | Token waste |
| Scope creep inside spawned block ❌ | Violates RCCF freeze |
