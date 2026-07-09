# `.claude/` — SOFI AI, ported from `.opencode`

This folder is a **faithful port of the `.opencode/` organisation into native Claude Code**:
**105 agents · 15 rooms · 1 Boardroom · 1 Gateway · 9 gates.** Everything OpenCode ran —
agents, skills, tools, commands, and the engine (constitution, registry, lifecycle,
governance, operations) — is reproduced here in the formats Claude Code discovers, so
opening Claude Code at the repo root just works.

**Source of truth is [`../CLAUDE.md`](../CLAUDE.md)** — it auto-loads on open and explains the team.
This README maps the folder.

---

## Layout

```
.claude/
├── agents/<room>/<room>-<role>.md   105 subagents, grouped by room (spawn by `name`)
├── skills/<room>-<role>/SKILL.md    107 skills (type `/` to run) → point at .claude/tools/
├── tools/<room>/<role>/…            105 per-role scripts (bash/python) the skills call
├── commands/*.md                    54 slash-command workflows (flat — Claude requirement)
├── engine/                          the operating system
│   ├── identity/                    constitution.md, org-chart.md
│   ├── agents/                      registry.yaml (rooms→roles), prompts/ (shared identity)
│   ├── governance/                  rules.yaml, fast-track.md, superpowers.md
│   ├── lifecycle/                   gates.yaml, checklists/gate-0..8.md, templates/
│   ├── operations/                  delegation, routing, verification, handoff, …
│   ├── monitoring/                  decisions, handoffs, evolution
│   └── hooks/                       pre-tool.sh, post-tool.sh (OpenCode-side, reference)
├── settings.json + hooks/*.py       Claude-native session hooks (security/git guard, brain inject)
├── sofi.json                        workspace manifest
└── docs/                            reference guides + archived design notes
```

## Port mapping (how OpenCode became Claude-native)

| OpenCode | → | Claude Code |
|----------|---|-------------|
| `.opencode/agents/<room>/<file>.md` (no `name`, `model: opencode/big-pickle`) | → | `.claude/agents/<room>/<file>.md` with `name:` added, `model: inherit` |
| `.opencode/skills/<room>/<role>/SKILL.md` | → | `.claude/skills/<room>-<role>/SKILL.md` (unique dir = `/command`), frontmatter added |
| `.opencode/tools/<room>/<role>/*.sh` | → | `.claude/tools/<room>/<role>/*.sh` (verbatim; skills reference the rewritten path) |
| `.opencode/commands/*.md` | → | `.claude/commands/*.md` (flat) |
| `.opencode/engine/**` | → | `.claude/engine/**` (internal `.opencode/`→`.claude/` paths rewritten) |
| `opencode.json` `instructions[]` + `agent{}` | → | `CLAUDE.md` (summary) + `engine/agents/registry.yaml` |

## How to use

1. **Open Claude Code at the repo root** → `CLAUDE.md` loads → the session knows the team.
2. **Run a workflow:** `/new <idea>` (full 9 gates) or a per-room command like `/bck-new <task>`.
3. **Spawn an agent by name:** e.g. `bck-api-engineer`, `arc-lead`, `brd-ceo`.
4. **Flat delegation:** the main session *wears* the CEO/Lead personas and spawns leaf specialists in one hop; subagents never nest. Contract: `engine/operations/delegation.md`.
