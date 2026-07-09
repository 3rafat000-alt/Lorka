# `.claude/` — SOFI AI team, native to Claude Code

This folder makes the **SOFI AI** enterprise run natively inside Claude Code:
**105 agents · 15 rooms · 1 Gateway · 1 Boardroom · 9 gates.** It mirrors the
`.opencode` organisation so the same team works here without any extra runtime.

**Source of truth is [`../CLAUDE.md`](../CLAUDE.md)** — it auto-loads when you open
Claude Code at the repo root and tells the session *who the team is and how it works*.
This README just maps the folder.

---

## What's here

| Path | What it is |
|------|-----------|
| `../CLAUDE.md` | Auto-context entry point. Read first. Flat topology, room table, 9-gate lifecycle, RCCF delegation, routing, constitution. |
| `agents/` | **105 subagents**, one file per agent, named `<room>-<role>.md` (e.g. `bck-api-engineer`, `brd-ceo`). Spawn any by its `name`. |
| `commands/` | **54 slash-command workflows.** Type `/` in Claude Code — `/new`, `/fix`, `/rm`, `/gate-check`, `/parallel-build`, `/deploy`, per-room `-new\|-fix\|-rm`, and sweeps. |
| `protocol/` | The operating system: `identity/` (constitution, org-chart), `registry.yaml`, `roster.md`, `lifecycle/` (9 gates + checklists + templates), `governance/` (rules, fast-track), `operations/` (delegation, routing, verification, handoff, …). |
| `hooks/` | Fail-open Python hooks wired in `settings.json`: PreToolUse security/git guard · SessionStart brain injection · PostToolUse checkpoint nudge · Stop breadcrumb. |
| `settings.json` | Hook wiring + SEO skills disabled. |
| `sofi.json` | Workspace manifest (agents path, project map, ignore rules). |
| `docs/` | Reference guides and archived design notes (historical — not the live contract). |

The deterministic toolchain the team leans on (the `sofi` dispatcher, scanners, the
verify gate) lives at repo-root `engine/`; see `CLAUDE.md` §7.

---

## How to use it

1. **Open Claude Code at the repo root.** `CLAUDE.md` loads automatically — the session now knows the team.
2. **Run a workflow:** type `/new <idea>` for the full 9-gate lifecycle, or a per-room command like `/bck-new <task>`.
3. **Or spawn an agent directly by name**, e.g. the Backend API engineer is `bck-api-engineer`, the coordinator is `brd-ceo`.
4. **One rule to remember:** delegation is flat — the main session *wears* the CEO/Lead personas and spawns leaf specialists in one hop; subagents never nest. Full contract in `protocol/operations/delegation.md`.

The authoritative agent list is `protocol/registry.yaml` (15 rooms → roles). The
9-gate lifecycle and per-gate exit checklists are in `protocol/lifecycle/`.
