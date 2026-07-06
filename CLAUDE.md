# CLAUDE.md — SOFI AI workspace (auto-context)

SOFI AI = autonomous AI software enterprise. 30 agents (29 specialists across 5 tiers + 1 CEO), 9-gate lifecycle. Doctrine: **Design is Truth · few token do trick · big brain small mouth.** Every delegation is a 4-part **RCCF** block — Role · Context · Command · Format (`engine/protocols/01-delegation-rccf.md`). 🪨

## Boot
Constitution: `.claude/SOFI_SYSTEM_PROMPT.md` (v5.0). Team: `engine/ROSTER.md`. Flow: `engine/lifecycle/gates.md`. Cost map: `engine/routing/routing.yaml`. Git law: `engine/protocols/git-discipline.md`. Token efficiency: `.claudeignore` (excludes vendor/node_modules/.git — ~80% context reduction). OODA engine: `engine/ooda/engine/main.py`.

## Run agents
Spec per role: `engine/agents/**` (Operating Prompt inside each). Spawnable Claude Code subagents: `.claude/agents/sofi-*.md` — delegate by name, e.g. `sofi-ux-researcher`; each is structured **RCCF** (🎭 Role · 📂 Context · 🎯 Command · 📐 Format) over its Operating Contract (gate · consume · produce · gate-bar · handoff · escalate) — read it before delegating. **Every spawn is a 4-part RCCF block** (`engine/protocols/01-delegation-rccf.md`); generate one with `/sofi-delegate <agent> <task>`. Drive a project via `engine/RUNBOOK.md`. **Flat topology (binding, `01-delegation-rccf.md` §0):** the *main session* is the only context that can spawn — a subagent cannot spawn subagents, so `sofi-ceo` and the tier-advisors are personas the main session **wears**, never live orchestrators; delegation is one hop (main → leaf specialist), and parallelism = several spawns in one message. The full raw-ask → coordinated-work flow (reception → CEO → tier-advisor → leaf, all one context wearing masks in sequence, spawning leaves in parallel, faking depth with rounds not nesting) is `engine/protocols/02-intake-orchestration.md`.

## Session lifecycle (hooks + skills — auto-wired)
Hooks in `.claude/settings.json` (all fail-open, code in `.claude/hooks/`): **PreToolUse** = security/git guard (blocks dangerous commands, `.env`, bad commit format); **SessionStart** = injects the active project's brain (STATE head + next ticket — no blind start); **PostToolUse** = nudges to `sofi checkpoint` when the tree drifts uncommitted; **Stop** = logs a session breadcrumb to `.claude/memory/sessions.jsonl`. Invokable skills (`/name`): **`/sofi-intake`** (reception — reformulate a raw/messy ask into a frozen intent brief before the CEO reasons; the front door, `engine/protocols/02-intake-orchestration.md`), **`/sofi-boot`** (orient), **`/sofi-gate`** (gate-bar check & advance), **`/sofi-handoff`** (record work the disciplined way), **`/sofi-team`** (who-to-spawn), **`/sofi-delegate`** (build a paste-ready RCCF spawn block for any agent). **Power tools** (flexible, token-frugal, grep-first): **`/sofi-audit <layer>`** (comprehensive layered inspection — ui/blade/css/js/db/api/integration/agents/all), **`/sofi-spec-review "<feature>"`** (architect 4-pillar feature review — Data&Logic · Admin&Ops · UI/UX&Taste · Edge-cases, Python-scanned; enforces the **7 steel rules** + SEV-report-first, binding protocol `engine/protocols/spec-review.md`), **`/sofi-feature "<feature>"`** (the big one — full loop on one feature: Python scan → review → fix → verify → report → gate → handoff), **`/sofi-secure <mode>`** (security squad — threat/pentest/scan/verify, wires the cyber-* skills), **`/sofi-fix <target>`** (route findings → cheapest specialist → checkpoint each), **`/sofi-report <kind>`** (durable evidence-backed writeup to the brain). Loop: **audit/secure → fix → report → gate → handoff**. These operationalize the universal contract below.

## Operating system (every agent obeys)
Protocols in `engine/protocols/` — read `00-operating-system.md` first; it's the universal contract. The others teach context/memory, research+internet, thinking+work, handoff+interconnection, tooling.

## v5 — the integrity & intelligence layer (binding)
v4 built the structure; v5 adds the layer that makes agents grounded, verified, and self-improving. Three doctrines bind every agent, on top of the universal contract: **`grounding.md`** (ground or abstain — cite every claim to file:line/brain/commit, paste execution proof, say "I don't know" out loud, surface conflicts); **`verification.md`** (outcome over self-report — a gate advances only on a fresh-context adversarial check against the *original* criteria + pasted mechanical evidence, never the implementer grading itself); **`reflection.md`** (`/sofi-reflect` distils HANDOFFS history into `_context/LESSONS.md` procedural memory, scheduled not per-turn). Support: structured queryable brain (`sofi brain-query`, memory-type frontmatter), budgeted-autonomy + effort-scaling (`routing.yaml` `effort_scaling`), RCCF v2 (clarify-before-commit, frozen brief, evidence block). Design record: `.claude/docs/v5/SOFI-V5-ARCHITECTURE.md`; the frontier research it's grounded in: `.claude/docs/ai-guides/research/`.

**Universal contract (before acting):** `sofi sync <PRJ>` (git orient — never blind) → read `projects/<PRJ-ID>/_context/STATE.md` (note `branch`+`head_sha`) → your ticket in `HANDOFFS.md` → `CONTEXT.md`. **After acting:** write artifact → `sofi checkpoint <PRJ> "<type>: ..."` (commit early/often) → append `CONTEXT.md` (+`DECISIONS.md` if irreversible) → update `STATE.md` (`head_sha`) → write next ticket in `HANDOFFS.md`. Uncommitted session = invisible to the next one.

## Memory system (routing ≠ behavior)
`MEMORY.md` (root) = the routing map — "where do I find X?" — pointers only; consult it before searching the vault blindly. This file stays the behavior contract; never store content in either. **Write trigger:** the word **«تذكّر» / "remember"** is the only trigger for durable doctrine/preference writes (this file, `MEMORY.md`, harness memory). Project-brain writes (`STATE/CONTEXT/DECISIONS/HANDOFFS`) stay contract-driven — unchanged. A policy change touches its ONE owning file, never fanned across files.

## Company brain
Live state per project: `projects/<PRJ-ID>/_context/{STATE,CONTEXT,DECISIONS,HANDOFFS}.md`. Isolated by `PRJ-ID`. 

**Directory layout (single physical root — NO symlink, 2026-07-03):**
- `~/Desktop/Lorka/` = SOFI framework (this repo, git)
- `~/Desktop/Lorka/projects/` = the ONE physical projects root (each `PRJ-XXXX/` is its own git repo; the brain `_context/` lives inside it). Tooling resolves it via `sofi_tools.paths.projects_dir()` (env `SOFI_PROJECTS_DIR`, else `~/Desktop/projects` if present, else this in-repo fallback — never a symlink). `sofi checkpoint` commits the brain in the project's OWN repo.

Scaffold a new project: `bash engine/bin/new-project.sh PRJ-XXXX "title" PRIORITY <date>` — this also **registers the project's local domain** `<slug>.local`.

## Local domain (first build step — binding)
Every project gets a clean local URL `<slug>.local` (e.g. `sakk.local`) — NOT raw `127.0.0.1:PORT`. `new-project.sh` auto-runs `sofi domain register`; the first squad that serves the app runs `sofi domain up <PRJ>` to bring it online. The URL+port live in `STATE.md` (`local_domain`/`local_port`). One-time host setup: `sofi domain init`. Full rules: `engine/protocols/local-domains.md`.

## Public tunnel (share the local app — bounded, owner = DevOps Lead)
Need the local app reachable from outside (client demo, UAT on a phone, a 3rd-party webhook)? `sofi tunnel up <PRJ>` gives `<slug>.local` a temporary public URL (cloudflared preferred, localtunnel fallback) by pointing the client at Caddy `:80` and forcing the project's Host — no vhost edits. URL is stamped into `STATE.md` (`public_url`). `sofi tunnel down <PRJ>` tears it down. **Security: publishes a dev app to the open internet with no auth — seed data only, no secrets/PII/prod data, kill it when done. A tunnel is not staging/prod (those are still Gates 6–7).** Full rules: `engine/protocols/public-tunnels.md`.

## Tooling (scripts & libraries)
Every Bash-holding role works through `engine/tooling/`. Law: `engine/tooling/GOVERNANCE.md`. Discover before writing: `engine/tooling/registry.yaml`. Shared library `sofi_tools` (brain·tickets·routing·gates·guard·runlog) + dispatcher `engine/tooling/bin/sofi` (`projects`·`brain`·`route`·`gate-check`·`dispatch`·`squad`·`powers`·`handoff`·`escalate`·`scratch`·`sync`·`checkpoint`·`claim`·`release`·`worktree`·`gate-merge`·`gate-tag`·`git-check`·`domain`·`tunnel`·`tools`·`doctor`). Per-role tools in `engine/tooling/agents/<tier>/<role>/`. One-off scripts → `projects/<PRJ>/_scratch/` (ephemeral, purged at gate exit, never a deliverable). Scripts write only inside their own project; net only if the role holds Web tools; exit 0/≠0 gates the pipeline.

## External review desk (Gemini — second opinion, automated loop)
Any report/spec worth a second architectural opinion goes through the **review desk**: `sofi gemini review --prj <PRJ> --json --text "<report+context+ask>"` — Python sanitizes (redacts keys/secrets/.env), condenses (weak-net safe), pushes to the pinned Gemini chat, captures the reply (re-captures not re-posts on timeout), parses into sections+action_items, and ingests a digest into `HANDOFFS.md`. **Binding loop:** compose the report INLINE (no `.md` authoring), request detailed guidance, then ANALYZE + EXECUTE the reply autonomously — don't stop to ask; repeat until done. `sofi gemini capture` resumes a timed-out capture; `sofi gemini status` probes. Tooling: `engine/tooling/agents/ceo/gemini_review.py` over `gemini_bridge.py`. Doctrine: *big brain small mouth* — the conversation carries only the distillate. External service: **sanitized only, never secrets/PII/prod data.** Full rules: `engine/protocols/external-review-desk.md`.

## Superpowers (external power-ups)
Vetted open-source capabilities the team plugs in — registry: `engine/SUPERPOWERS.md`. Headlines: **FossFLOW** (isometric architecture diagrams → architects, Gate 3), **taste-skill** (anti-generic-UI design dials → designers/frontend, Gate 2/4), **The Agency** (org-structure patterns: escalation chains, parallel squads, per-role success metrics). Powers go proposed → piloted → promoted; promotion = row in `registry.yaml` + `DECISIONS.md`. No power overrides a gate bar; code/security never compressed.

## Internet
Research/architecture/security/ops roles hold `WebSearch`+`WebFetch` (see `engine/protocols/tooling-matrix.md`). Devs stay on the frozen contract; pull web findings via their lead. Ladder: brain → codebase → search → fetch → verify → cite.

## Routing — economic grid (always pick cheapest that clears bar; log route in thinking)
Ladder (escalate on evidence only): 🟢 → 🔵 → 🔮 → 🟣.
- 🟢 `haiku` (Haiku 4.5) — **first line, 80% of routine ops**: light queries, single-file reads, format checks, carved commands, boilerplate, manual QA, commits.
- 🔵 `sonnet` (Sonnet 5) — **second line**: clear-cut coding beyond haiku — simple feature code, Blade views, side migrations, tests, reviews.
- 🔮 `fable` (Fable 5) — **gatekeeper**: cross-layer full-stack sweeps only — `/sofi-spec-review` hard gate (7 steel rules + Tier-A), race conditions, tangled webhooks, architectural arbitration.
- 🟣 `opus` (Opus 4.8, 1M ctx) — **last resort**: repo-wide deep debugging on unknown-source total failures. **Forbidden for routine code-writing.**
- `/sofi-spec-review` two-phase: grep sweep + SEV draft on haiku/sonnet → full context handover to Fable 5 for the hard gate (steel-rule match, Tier-A check, final report + approval).
- Caveman `lite|full|ultra` for chatter. **Code, commits, security warnings = normal prose, never compressed.**

## Gate order (no skip)
0 Inception → 1 Discovery → 2 Design → 3 Architecture → 4 Build → 5 Quality → 6 Staging/UAT → 7 Prod → 8 Observe→loop.

## Rules
- Every feature traces to a Journey Map stage, else → Backlog.
- Projects isolated by `PRJ-XXXX`; no cross-project bleed.
- Reusable code → `.claude/shared-packages`, never duplicated.
- Migration without rollback = rejected. Coverage <90% = rejected. TTI ≥2s = rejected.
- Git is the spine: orient with `sofi sync`, checkpoint every milestone, hand off a recorded `head_sha`. Project work on `prj/<ID>` (parallel squads in worktrees); doctrine on `main`. No blind start, no uncommitted handoff, no secrets/`_scratch/` in history, no `reset --hard`/`--force` (hook-blocked).

## Stack defaults
Backend Laravel/PHP · Web Blade+Vue3+Tailwind · Mobile Flutter/Bloc · CI/CD Harness · Obs Prometheus/Grafana/Sentry.
