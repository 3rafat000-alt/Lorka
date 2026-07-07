# SOFI v6 Pattern Library — Synthesis of GitHub Multi-Agent Research

> **What this is:** the evidence base for SOFI v6. 13 parallel research agents swept GitHub's most-recently-updated `claude` repositories (frameworks, agent/skill collections, orchestration harnesses, memory systems, routing layers) and distilled the architectural patterns for a 100+ agent AI software company. Every claim is attributed to real repositories.
>
> **How to read it against our build:** the **convergence note** at the bottom is the headline — independent projects arrived at the same doctrines SOFI already carries (`03-verification.md`, `04-reflection.md`). The delta v6 must build is not the doctrine but its **mechanization**: hooks that block (not nudge), schemas that lint, budgets enforced at the spawner, routers that are eval-gated code, and a brain that is indexed, tiered, decaying, and self-surfacing. The staged plan lives in `company/brain/org/EVOLUTION.md`.

Target: 100+ agent AI software company in a Claude Code repo — rooms/departments, connecting nexus, brain/memory, token frugality. Patterns ranked by architectural value; every claim attributed.

---

## 1) Top 15 Patterns

### P1. Room = Installable Plugin (load only the department you enter)
**Mechanism:** Package each department as a Claude Code plugin: `plugins/<room>/{.claude-plugin/plugin.json, agents/, commands/, skills/, hooks/hooks.json, bin/}`. Components auto-discover from directory structure; installing/enabling a plugin loads ONLY its components into context. Plugin name is a free collision-proof namespace (`room-payments:auditor`, `/room-qa:regress`). Executables in `bin/` join the Bash PATH while enabled — the sanctioned way to ship a per-room CLI.
**Sources:** wshobson/agents (88 plugins, 194 agents), VoltAgent/awesome-claude-code-subagents (10 numbered category dirs = 10 plugins), official plugins-reference spec, obra/superpowers-marketplace.
**Apply:** Restructure LORKA as `rooms/<name>/` plugins with one `marketplace.json` catalog at repo root. A session activates 1–2 rooms, never the whole company. The filesystem IS the org chart (numbered dirs, VoltAgent-style). The `sofi` dispatcher ships via `bin/` of a core "nexus" plugin.

### P2. Three-Level Progressive Disclosure (the core token economy)
**Mechanism:** L1: only frontmatter `name`+`description` resident at boot (~few dozen tokens/agent or skill — hundreds cost almost nothing). L2: body loads only when the description matches the task. L3: sibling reference files/scripts load only when the body points at them. Description is a **router key** ("Use when X. Produces Y."), never a workflow summary — agents follow summaries instead of reading the skill (tested failure mode).
**Sources:** anthropics/skills (spec + pdf skill reference impl), obra/superpowers (writing-skills), pm-claude-skills (454 skills routed on frontmatter only), rsmdt/the-startup (~100 tokens of names at startup), wshobson.
**Apply:** Every LORKA agent/skill gets a trigger-form description, per-frequency word budgets (frequently loaded <200 words, others <500 — superpowers), heavy reference split into on-demand files, cross-references via lazy name markers (`REQUIRED SUB-SKILL: room-x:y`) — never `@`-includes.

### P3. No Inter-Agent Chat — Artifacts and Status Fields Are the Only Channel
**Mechanism:** Agents never message each other. Each task writes deterministic outputs (branch, SHA, PR URL, token usage) to a status record; downstream tasks declare `dependsOn` and template upstream results in (`{{.Deps}}`). Peer-to-peer chatter explicitly banned; hub-and-spoke through one orchestrator entry point. Communication becomes auditable, replayable data flow. Pub-sub variant: roles subscribe to upstream **artifact types** (Architect wakes on PRD published) so no central router enumerates 100 agents — the artifact type is the routing key.
**Sources:** kelos-dev/kelos, Automaat/sybra, vanzan01/claude-code-sub-agent-collective, lst97, FoundationAgents/MetaGPT (pub-sub message pool), yohey-w/multi-agent-shogun.
**Apply:** The LORKA nexus is a data plane, not a chat room: HANDOFFS tickets carry structured fields (branch, head_sha, artifacts[], tokens), and rooms subscribe to artifact types crossing gates. Room-scoped channels + explicit @mentions + event-driven wake only when needed (AI-company, agent-teams-ai nudges) — idle agents cost zero tokens.

### P4. Deterministic Non-LLM Orchestration — Tokens Only for Judgment
**Mechanism:** The scheduler is plain code: one LLM call decomposes the plan into an inspectable DAG artifact; routing, dependency resolution, retries, serialization, and merges are deterministic Python. Bernstein burns **zero** tokens on coordination and gets byte-identical replay from a Merkle-chained journal.
**Sources:** sipyourdrink-ltd/bernstein, open-multi-agent/open-multi-agent (plan-as-artifact + deterministic scheduler), kelos (controller = code).
**Apply:** Grow `engine/tooling/bin/sofi` into the nexus scheduler: `sofi plan` (one Fable call → frozen DAG in the brain), then `sofi run` executes it mechanically — dispatch, gate checks, queue, merges all scripted. Single biggest token lever at 100-agent scale.

### P5. Fresh-Context Verifier — Implementer Never Grades Itself, Structurally
**Mechanism:** A separate verifier agent with fresh context and read-only tools grades work against the *original* criteria. Strongest variants: blinded auditor that runs gates but **cannot see the implementation** (autonomous-work-harness), a dedicated veto department hard-wired as unskippable pipeline stage with sole rejection authority (edict's menxia), parallel validator fan-out per gate (5 validators on tech-spec, 3-iteration cap — molyanov). Validator math: 5 steps × 80% = 33% end-to-end; validator+retry per step = 99% (AgentHub). Reviewer findings are hypotheses until adversarially confirmed — engineer against reviewer hallucination too (Himmel's verify-before-critical).
**Sources:** Connected-Mate/cognitive-night, miro77/autonomous-work-harness, cft0808/edict, pavel-molyanov/molyanov-ai-dev, disler/claude-code-hooks-mastery (builder/validator pairs), yotamleo/Himmel, wshobson (verify never on the cheap tier).
**Apply:** Validates SOFI v5 `verification.md` — upgrade it: (a) verifier agents get `Read,Grep,Glob` only; (b) a "Menxia room" sits on every gate with veto-only power + veto-loop counter escalating to human; (c) validators run in parallel fan-out, capped at 3 rounds.

### P6. Mechanical Gate Enforcement in the Hook Layer (doctrine → impossibility)
**Mechanism:** Exit-code-2 blocking protocol: PreToolUse/Stop/SubagentStop/UserPromptSubmit hooks can block, stderr fed back as corrective instruction. Stop-hook proof gate: if files changed, the turn cannot end until the transcript contains executed gate-script output at the exact working-tree hash — self-reported success is structurally impossible. Anti-deadlock: block-count cap + progress check so gates can't trap a stuck session. State machine rejects illegal gate jumps (`_VALID_TRANSITIONS`); a runtime permission matrix whitelists who may message whom. Progressive enforcement: soft reminder → strong reminder → hard block.
**Sources:** miro77/autonomous-work-harness (stop-require-gates), disler/claude-code-hooks-mastery, OthmanAdi/planning-with-files, cft0808/edict, Stanshy/AgentHub (Stop requires passing tests), alfredolopez80/multi-agent-ralph-loop (4-stage gate on TeammateIdle/TaskCompleted), CronusL-1141/AI-company.
**Apply:** Convert SOFI's fail-open hooks to graduated fail-closed: gate order as a transitions table in `sofi gate-check`, Stop hook demanding pasted `record-gates` proof, org chart doubling as a communication ACL enforced at hook time.

### P7. Context Collapse — Fixed-Schema Handoffs, Never Transcripts
**Mechanism:** Replace a subtask's raw history (50k tokens) with a fixed-schema handoff: Changed Files · Relevant Reads · Commands+outcomes · Failures · config used. Full transcript survives on disk for forensics; the receiving agent is **explicitly forbidden** from re-reading logs. Context-budget packets (`context_NNN.md`) condense prior rounds to exactly what the next agent needs. Orchestrator context grows by a fixed size per subtask, not by subtask effort.
**Sources:** nicobailon/pi-boomerang, WenyuChiou/agent-collab-skills, kelos ({{.Deps}} typed results), preset-io/agor (fork=inherit vs spawn=clean as distinct primitives).
**Apply:** Make HANDOFFS.md tickets schema-enforced (lint the fields), ban transcript replay in the RCCF contract, and adopt fork/spawn vocabulary: forks inherit brain context, spawns get only the frozen RCCF brief + handoff packet.

### P8. Worktree-per-Task Isolation + Janitor-Gated Serialized Merge Queue
**Mechanism:** Every agent works in its own git worktree (auto port allocation, own session history — agor); main stays pristine. A non-LLM "janitor" verifies concrete completion signals (tests pass, files exist, lint/types clean) before a serialized merge queue lands work — no races by construction. Parallel implementers get disjoint **file-ownership boundaries**. Same-branch tasks auto-serialize (free mutex — kelos). At swarm scale with no coordinator: a `coordination/` dir of lock files + work registry that agents honor by protocol, stale locks auto-recovered >2h.
**Sources:** sipyourdrink-ltd/bernstein, preset-io/agor, Yeachan-Heo/oh-my-claudecode, wshobson agent-teams, Dicklesworthstone/claude_code_agent_farm, garrytan/gstack (10–15 parallel worktrees).
**Apply:** Make `sofi worktree` the default for every ticket (not the exception); `sofi gate-merge` becomes a janitor script checking mechanical signals before merge; squad spawn configs declare file-ownership boundaries.

### P9. Layered Memory with a Budgeted Wake-Up (survive /clear for <7k tokens)
**Mechanism:** Stratify memory so SessionStart injection has a hard token budget: L0 identity → L1 essential distilled rules → L2 learned rules taxonomy (`halls/rooms/wings`) → L3 vault reachable only by on-demand grep. Ralph-loop wakes on **818 tokens**; shogun engineers full post-/clear recovery in 2 file reads (~6,800 tokens). Design rule: treat the session as expendable; everything needed to resume is reachable in ≤2 reads.
**Sources:** alfredolopez80/multi-agent-ralph-loop, yohey-w/multi-agent-shogun, keli-wen/agentic-harness-patterns (3-tier trust model), open-gsd/gsd-core (STATE/CONTEXT as the only bridge).
**Apply:** Restructure the SOFI brain injection: SessionStart injects a fixed-budget digest (identity + STATE head + next ticket, ≤1k tokens); everything else is L3 via `sofi brain-query`. The halls/rooms/wings taxonomy maps literally onto LORKA rooms.

### P10. The Harness Remembers — Hook-Captured Memory Pipeline
**Mechanism:** Memory writes never depend on agent discipline: PostToolUse captures observations, SessionEnd AI-compresses into SQLite(+search index), SessionStart injects a compact digest. Retrieval is 3-layer progressive disclosure: 50–100-token ID index → timeline → fetch full records by ID (~10x savings). Corrections captured as `[LEARN]` blocks by a Stop hook into FTS5 SQLite, auto-injected at UserPromptSubmit **only on topical match** — memory surfaces itself when relevant.
**Sources:** thedotmack/claude-mem (86k stars), rohitg00/pro-workflow, affaan-m/ECC, mnemon-dev/mnemon (deterministic Go engine, LLM only for judgment calls).
**Apply:** Upgrade LORKA's Stop-hook breadcrumb into a capture→compress→inject pipeline over one SQLite brain index; add topical auto-injection at UserPromptSubmit (the piece SOFI's brain lacks). Keep the LLM out of the write path (mnemon model): deterministic storage/index/decay, model only decides remember/link/recall.

### P11. Learning Promotion Pipeline with Thresholds, Confidence, and Decay
**Mechanism:** Learning is a scheduled hook chain, never per-turn. Concrete numbers to steal: confidence-scored instincts, inject max 6 above 0.7 confidence, 8000-char cap, promotion path lesson→instinct→skill (ECC); errors cluster in a ledger, promote to global at 5+ occurrences across 2+ projects, permanent rule at 10× — 46% of auto-learned rules dropped as duplicate noise (vibecosystem); learnings decay 5%/week, auto-promote after 3 successful uses (gstack); "Failure Alchemy" stores each root cause 3 ways — searchable antibody, auto-injected pre-task vaccine on pattern match, system-prompt catalyst (AI-company).
**Sources:** affaan-m/ECC, vibeeval/vibecosystem, garrytan/gstack, CronusL-1141/AI-company, Yeachan-Heo/oh-my-claudecode (/skillify with quality gates).
**Apply:** Upgrade `/sofi-reflect`/LESSONS.md from append-only log to managed cache: confidence scores, injection caps, occurrence-threshold promotion, decay, and a vaccine path that auto-injects a matching lesson into the RCCF brief of an incoming task.

### P12. Cost Ladder as Data: Tier in Frontmatter + Zero-Cost Router + Acceptance Cascade
**Mechanism:** (a) Model tier stamped in every agent's frontmatter (`model: haiku|sonnet|opus|inherit`) so routing travels with the definition — wshobson publishes the census (Haiku 20 / Sonnet 62 / Opus 54 / Fable reserved). (b) Routing itself costs ~zero: local heuristic/embedding classifiers (<1–10ms), never an LLM judging; deterministic override rules run BEFORE the classifier (security/cross-layer → force top tier by RULE). (c) Cascade with post-generation verifier: try cheap, machine-score the response (refusal/truncation/parse-fail vs threshold 0.80), escalate on evidence — "escalate on evidence only" made mechanical. (d) Routers are eval-gated code (compass: 96.9% accuracy corpus; UncommonRoute: execution-verified labels, 75/100 SWE-bench at 53% cost; track downgrade rate as the KPI). (e) Thinking/effort is a routed resource too — per-category reasoning on/off in config. Named choreography: expensive plans → cheap executes → expensive verifies; verify never on the cheap tier.
**Sources:** wshobson/agents, VoltAgent, dshakes/compass, lm-sys/RouteLLM, NadirRouter/NadirClaw, BlockRunAI/ClawRouter, CommonstackAI/UncommonRoute, vllm-project/semantic-router, katanemo/plano (routing/guardrails/metering as one proxy plane below all agents).
**Apply:** Keep `routing.yaml` but: stamp tier in each `sofi-*.md` frontmatter, add hard override rules for the `/sofi-spec-review`-class categories, add a cheap-tier acceptance verifier to `sofi route`, and recalibrate the table quarterly from the (task-class, tier, gate-passed?) ledger in HANDOFFS history.

### P13. Budgets Enforced at the Spawning Layer, Not by Agent Discipline
**Mechanism:** Caps live where work is created: maxConcurrency, maxTotalTasks, per-task deadlines, suspend/resume brake (kelos); hard 3-agent concurrency cap + cron heartbeat watchdog + fixed escalation ladder (retriable→todo, stuck→human, repeated→interactive) (sybra); round-capped fix loops (×3 then mandatory human handoff — compass); spend caps with graceful degradation to cheapest tier, and "I am low-confidence" as a first-class escalation trigger (UncommonRoute); phase turn caps in declarative config so no phase can loop forever (ChatDev); convergence rule banning pure-discussion cycles after cycle 2 (auto-company); monitor context % and auto-/clear below threshold (agent_farm).
**Sources:** kelos, Automaat/sybra, dshakes/compass, CommonstackAI/UncommonRoute, OpenBMB/ChatDev, nicepkg/auto-company, Dicklesworthstone/claude_code_agent_farm.
**Apply:** `sofi dispatch`/`sofi squad` carry mandatory budget fields (max agents, max rounds, token cap, deadline); a heartbeat file per squad; the escalation ladder is a table in the nexus, not prose.

### P14. Machine-Checkable Resume: Breadcrumb JSON + Spec-on-Disk + Frozen Briefs with Embedded Gates
**Mechanism:** After each stage write `breadcrumbs/<ticket>.json {ticket, branch, base_sha, head_sha, completed[], next_step}`; on resume classify FRESH (head_sha matches → deterministic resume) vs DEGRADED (stale → reconstruct from git log + demand confirmation, never resume silently). Specs persist on disk (`specs/<id>/requirements.md, plan/phase-N.md, receipts`) so a spec ID resumes work across full context resets. PRP pattern: the frozen brief embeds its own executable validation gates (test commands that must pass) — verification is mechanical, carried by the brief itself. Compaction is a planned event with pre/post recovery hooks, never an accident.
**Sources:** yotamleo/Himmel, rsmdt/the-startup, gmickel/flow-next (receipts: commits+tests+verdicts per task), coleam00/context-engineering-intro (PRP), molyanov (post-compact-restore.sh), ECC/pro-workflow (pre/post-compact hooks), gstack (WIP-commit context + /context-restore).
**Apply:** Upgrade STATE.md's prose `head_sha` to breadcrumb JSON with a FRESH/DEGRADED resolver in `sofi sync`; RCCF v2 briefs embed executable acceptance commands; PreCompact hook flushes brain state.

### P15. The Nexus Is Staffed and Addressable: Master Router + Meta-Orchestration Room + Fleet Telemetry
**Mechanism:** (a) One small always-resident **master-router skill** per room: fingerprint table + task→skill mapping + composition rules (exactly one exclusive base skill + additive layers; layers "never re-teach primitives") — the cheapest dispatch for 100+ capabilities. (b) Orchestration is a first-class department: agent-organizer, context-manager, task-distributor, error-coordinator, knowledge-synthesizer speaking a standard JSON protocol; hard cap of 1–3 specialists per task. (c) The orchestrator exposes itself back to agents as an MCP endpoint so a lead can spawn its own squad (agor). (d) Every hook event on every agent POSTs to one SQLite+WebSocket telemetry server → live fleet dashboard with per-session swimlanes — at 100 agents, hooks must emit as well as guard.
**Sources:** gamedev-skills/awesome-gamedev-agent-skills, VoltAgent category 09, lst97, preset-io/agor, disler/claude-code-hooks-multi-agent-observability, vibeeval/vibecosystem (73 sensor hooks injecting routing context).
**Apply:** LORKA's nexus = one router skill per room + a meta-orchestration room (ops product = other agents' throughput) + a `send_event.py` line in every room's hooks + eventually a `sofi mcp` endpoint for self-service delegation.

---

## 2) Agent-Definition Best Practices

- **Frontmatter is exactly 4 fields:** `name` (kebab-case), `description`, `tools`, `model`. Universal convergence across wshobson, VoltAgent, 0xfurai, lst97. The router never reads bodies — it routes on the frontmatter index alone.
- **Description = activation condition, third person, concrete symptoms**, ending with "Use PROACTIVELY when …". Never a workflow summary (tested failure: agents follow the summary instead of loading the body — obra/superpowers). Max ~500 chars. contains-studio adds 3–4 worked trigger examples with commentary in the description.
- **Least-privilege tool grants encode identity:** reviewers/validators `Read, Grep, Glob` only; implementers `Read, Write, Edit, Bash, Glob, Grep`; only research/architecture roles get `WebSearch/WebFetch`. Security boundaries scale with the roster automatically (VoltAgent's Tool Assignment Philosophy, disler builder/validator).
- **Model tier stamped per agent** (`model: haiku|sonnet|opus|inherit`), with written assignment criteria published in a docs census (wshobson docs/agents.md).
- **Uniform body template** at 100+ scale — agents become lintable rows: lean 4-section (focus areas / approach / quality checklist / output — 0xfurai) or full 11-section (wshobson). Two sections are load-bearing for org charts: **Workflow Position** (declared dependencies on named neighbor agents) and **Key Distinctions vs sibling roles** (prevents overlap).
- **Size:** quality floor of 500+ words system prompt (contains-studio); wshobson runs ~4,500 words for flagship agents; frequently-spawned agents lean smaller. Skills: <200 words if frequently loaded, <500 otherwise, <500 lines hard max (open-design); push heavy reference into sibling files and parameter docs into tool `--help`.
- **Spawned specialists get a byte-budgeted brief, never the full constitution** — SubagentStart caps injected rules (60 lines / 2 actions — AI-company); three-man-team's 5 token rules live in CLAUDE.md.
- **Agent configs are tested code:** lint with agnix/`claude plugin validate --strict` in CI; eval harness on the roster itself (static lint + LLM judge + Monte Carlo — wshobson plugin-eval); TDD for skills — reproduce the failure before writing the skill (obra); version-pin and SHA-256 content-pin against drift (pm-claude-skills, antigravity).
- **Single markdown source, compiled to N harnesses** (wshobson targets 6 runtimes) — write the org once.

## 3) Memory/Brain Best Practices

- **Three-tier trust model, tagged on every artifact:** instruction memory (human-curated, always loaded) > auto-memory (agent-written, loaded selectively) > session extraction (background-derived, retrieved on demand). Writes never cross tiers; verifiers weight evidence by tier (keli-wen/agentic-harness-patterns — matches grounding.md).
- **Four canonical context operations to structure the whole layer:** Select (just-in-time loading), Write (persist before compaction), Compress (planned, with pre/post state preservation), Isolate (delegation boundaries: Coordinator/Fork/Swarm topologies).
- **Fixed-budget wake-up:** SessionStart injects ≤1k tokens (identity + STATE head + next ticket); deeper layers lazy (ralph-loop's 818 tokens; shogun's 2-read recovery).
- **Section-level indexed retrieval, never file reads:** index brain files by heading into stable IDs with byte offsets + SHA-256 drift hashes; search returns summaries, fetch exact sections (~12,000→~400 tokens/lookup — jdocmunch). PostToolUse hook re-indexes after edits; keep a savings ledger. SQLite FTS5+BM25 beats a vector DB at this scale (bernstein deliberately has no vector store).
- **Typed brain files read on demand:** STATE/CONTEXT/DECISIONS/HANDOFFS validated by centminmod's memory-bank (add a troubleshooting file); plus a **memory-bank-synchronizer** role that audits brain-vs-code drift, and periodic `/cleanup-context` dedup (15–25% cut).
- **Single-writer rule:** every shared artifact (STATE.md, dashboards, LESSONS.md) has exactly one designated writer role; everyone else appends to their own file (shogun's karo, edict's shangshu). Kills write contention outright.
- **Memory is a managed cache, not an append-only log:** confidence scores, TTL/decay, outcome scoring (promote what worked, demote what failed), occurrence-threshold promotion, dedup filtering (gstack, ECC, vibecosystem, roampal/presence).
- **Two memory classes kept separate:** behavioral rules/corrections vs durable researched knowledge (claims-with-sources wiki plane — pro-workflow). Company knowledge vault ≠ per-project brain.
- **Accountability substrate:** append-only hash-chained JSONL per decision, attributable to an agent identity, replayable offline (bernstein — skip the heavy crypto, keep the shape).
- **Fork-safe shared state for parallel agents:** slug-isolated plan directories with SHA-256 attestation files routing every hook call to the right plan (planning-with-files).

## 4) Orchestration/Communication Best Practices

- **Hub-and-spoke, P2P banned; 1–3 specialists per task, teams capped at 2–4** (vanzan01, lst97, wshobson agent-teams). Handoff = previous agent's structured output as context, no shared mutable state.
- **Plan-as-artifact then deterministic execution:** one smart LLM call emits an inspectable DAG; code schedules it (bernstein, open-multi-agent). Complexity-tiered dispatch — direct / incremental / factory modes auto-selected from spec artifacts (the-startup); wave-based parallel dispatch over the dependency graph (molyanov).
- **Fork vs spawn as distinct primitives** with different context-hygiene semantics; full lineage tree queryable for provenance (agor).
- **File-based transport with nudge-only wake:** per-agent task/inbox files (flock-protected), watcher sends only "you have mail" — content never travels the channel; 3-phase escalation nudge→interrupt→/clear (shogun). Markdown-as-database with reactive file-watcher sync (AgentHub); hook-driven SQLite bus with mid-turn injection and 30s file-collision alerts as the upgrade (hcom).
- **Zones/gates as automation triggers:** moving work into a room fires that room's templated prompt (agor zones) — gate transitions ARE dispatches.
- **Typed SOP primitives instead of ad-hoc discussion:** meeting templates with fixed roles + required output artifact; debates as exactly 4 rounds Advocate→Critic→Response→Judge (AI-company); recipes/skill-chains as declared pipelines within a gate (pm-claude-skills).
- **Cross-model/committee second opinion on consequential decisions:** different-vendor reviewers with merged-findings output (gstack /review+/codex, compass second-vendor Auditor, flow-next SHIP verdicts — "different models make different mistakes"). Guard against **multi-agent echo**: differently-conditioned committee members, quantitative gauges not verdicts, human as final discriminator, exactly ONE persistent Main instance (lighthouse).
- **Escalation ladder as a fixed table** + heartbeat watchdogs + "committed-work-with-no-PR" gap detection (sybra); every headless agent MUST commit before finishing or its work is destroyed.
- **Event-driven agents beyond sessions:** CI-triggered agents (claude-code-action modes: mention/automation/assignment) and TaskSpawners turning issues/webhooks/cron into budgeted tasks (kelos) — Gates 5–8 run from repository events, not human sessions.
- **Persistent routing table written into project CLAUDE.md** by a team-configurator so agent selection survives sessions at zero re-analysis cost (vijaythecoder).

## 5) Token-Frugality Best Practices

- **Progressive disclosure everywhere** (P2): frontmatter-only discovery; on-demand bodies; per-frequency budgets; master-router skills as the only always-resident index.
- **Deterministic work in scripts, judgment in the model:** skills bundle `scripts/`; computation in stdlib helpers, never in-prompt (anthropics/skills, pm-claude-skills); CPU pays for context location — tree-sitter repo map, graph-ranked, under a hard `--map-tokens` budget (aider).
- **Zero-inference compression of tool outputs before they enter context:** content-type-gated pipeline (log folding, grep dedup, diff folding, JSON sampling, AST-aware compression that never renames identifiers), reversible via `[rewind:hash]` markers — 36% average reduction free (claw-compactor).
- **Fixed-schema handoffs, never transcripts** (P7); orchestrator context grows O(subtasks), not O(effort).
- **Fresh-context disposal beats compaction:** one slice per tick in a clean window, matrices/brain as the only inter-tick memory — cost per tick flat regardless of project size (autonomous-work-harness, gsd-core, flow-next "no token bleed").
- **When you must compact, preserve the cache:** trim the MIDDLE, keep head (system prompt + tools) and recent turns byte-for-byte — summarizing busts provider prompt caches; copy-on-write prefix reuse across agents sharing one constitution (~4.1x — fak). Strategic compaction at task boundaries with pre-compact snapshot hooks, never reactive at 95% (ECC).
- **Routing costs ~zero** (P12): local classifiers, hot-reloadable rule overrides, semantic cache as rung zero, **top-k tool-schema selection per request** instead of the full catalog (semantic-router — one of the largest silent savings for big tool registries).
- **3-layer memory retrieval:** ID index → timeline → fetch by ID (~10x — claude-mem).
- **Measure it:** per-hook latency/token profiling (claudekit), savings ledgers (jdocmunch), per-prompt token+dollar accounting (agor), honest cost warnings per orchestrated feature (vijaythecoder: 10–50k tokens).
- **Local CLIs over MCP servers** where possible (Himmel's Jira CLI) — no schema overhead per turn.

## 6) Anti-Patterns to Avoid

1. **LLM-as-coordinator:** burning model tokens on dispatch, queue management, or gate checks that code can do (inverse of bernstein/open-multi-agent).
2. **Free-form inter-agent chat / P2P messaging:** unauditable, token-hemorrhaging, order-fragile; every framework that scaled banned it (kelos, sybra, vanzan01, shogun).
3. **Self-graded completion:** any gate advanced on the implementer's report without fresh-context verification + mechanical evidence (universal; edict/autonomous-work-harness make it impossible, not just discouraged).
4. **Description-as-workflow-summary:** agents follow the summary and skip the skill body (obra, tested). Same family: `@`-includes that force-load files before needed.
5. **Whole-roster-in-context:** one monolithic `.claude/agents/` tree always loaded instead of room plugins + frontmatter routing (why wshobson/VoltAgent shard into plugins).
6. **Transcript-passing handoffs:** feeding a subagent's raw history to the next agent; also letting the receiver "re-search the logs" (pi-boomerang forbids explicitly).
7. **Reactive auto-compaction and summarize-to-compact:** loses state and busts prompt caches; compaction must be a planned gate event with recovery hooks (fak, ECC, molyanov).
8. **Uncapped loops and pure-deliberation cycles:** fix loops without round caps (compass ×3), phases without turn caps (ChatDev), discussion cycles without a forced GO/NO-GO (auto-company's convergence rule), verification loops without circuit breakers (cognitive-night).
9. **Budgets by agent self-discipline:** trusting each agent to self-limit instead of enforcing concurrency/spend/deadline at the spawner (kelos) — runaway loops are the #1 failure mode at 100+ agents.
10. **Trusting consensus among clones — multi-agent echo:** 30 identically-conditioned agents agreeing is weak evidence; also reviewer hallucination blocking merges unverified (lighthouse, Himmel).
11. **Silent resume from stale state:** resuming on a head_sha that no longer matches HEAD without DEGRADED-mode reconstruction and explicit confirmation (Himmel).
12. **Multiple writers to shared artifacts** (merge conflicts, quality bypass — shogun/edict's single-writer rule exists because of this) and **append-only memory that never decays** (noise accretion; vibecosystem dropped 46% of auto-learned rules as duplicates).
13. **Agent configs as untested prose:** unlinted frontmatter, unpinned skills that rot, hooks never held to a test corpus (agnix, compass's 61-case corpus, jeremylongshore's CI rubric) — and unreviewed third-party skills/hooks, which are the attack surface (trailofbits: backdoored skills exist in the wild).
14. **The frontier model routing itself:** an LLM call to decide which LLM to call (ClawRouter/NadirClaw/plano all route locally in <10ms).
15. **Everything-persistent sessions:** long-lived contexts degrading instead of disposable fresh-context workers born clean from the brain; more than one persistent "Main" instance holding continuity (gsd-core, lighthouse).

---
**Convergence note:** Independent projects (cognitive-night, autonomous-work-harness, edict, molyanov, AgentHub, wshobson) all arrived at SOFI v5's verification.md/reflection.md doctrines — the delta LORKA should build is not the doctrine but its **mechanization**: hooks that block, schemas that lint, budgets in the spawner, routers that are eval-gated code, and a brain that is indexed, tiered, decaying, and self-surfacing.