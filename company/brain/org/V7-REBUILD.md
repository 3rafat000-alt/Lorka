---
type: program-tracker
program: SOFI v7 rebuild
status: in-progress
started: 2026-07-07
recovery_tag: v6.1-recovery-pre-v7
mem: durable
---

# SOFI v7 Rebuild — Program Tracker

The living record of the v7 rebuild. Read this first on any session that continues the work.
The framework brain is NOT auto-injected at SessionStart (that hook serves the active *project*),
so this file is the only resumable state for framework-level work.

## Decision on scope (2026-07-07)
Owner asked for a "literal full rewrite from scratch" + connect-to-cloud (remote agents · dashboard
deploy · GitHub/CI · Gemini oracle). Evidence from the audit (below) showed **two-thirds of the
framework is reference-quality gold** (105 agents, nexus, constitution — perfect parity), and the rot
is concentrated in one legacy layer. So v7 is executed **surgically**: kill the dead, rebuild the
rotten, polish + unify the gold, add the cloud layer — same "legendary clean v7" result, without
throwing away proven work. v6 stays fully recoverable at tag `v6.1-recovery-pre-v7`.

## The audit that grounds this (2026-07-07)
33-agent read-only workflow, **646 files read**, 30 subsystems. Aggregate:
- 47 cruft candidates · 76 inconsistencies (17 HIGH) · 28 redundancies · 141 v7 recommendations.
- 🟢 GOLD (keep, use as templates): rooms 00/01/02/05/07/12 have exact spec↔spawnable↔registry↔routing↔gates parity.
- 🔴 ROT (concentrated): `engine/` (dead) · `company/os/toolkit/` legacy tier naming · OODA engine (broken) · autopilot (never ran) · `company/brain/org/` v5 files · doctrine drift in CLAUDE.md/registry/gates.
- Findings JSON archived this session at scratchpad `v7_findings.json` (ephemeral — re-run the workflow to regenerate: script at `.../workflows/scripts/sofi-v7-audit-*.js`).

## ✅ RESOLVED — was highest priority
1. **GitHub PAT leak** — ✅ **REVOKED by owner (2026-07-08)**. Working code fixed to env var (5a567a3);
   the leaked `ghp_…` value is now dead, so the historical blob in commit 2ba6be6 is inert (no history
   scrub needed). The 25 v7 commits are pushed to origin and GitHub Actions CI runs green. Any future
   credential goes in GitHub Secrets, never the code.
2. **Spawnable `tools:` frontmatter is inconsistent + gets clobbered** — some of the 105 use a
   YAML-map `tools:` block, ~20 omit it entirely (→ all-tools default), and a transient agent (an
   audit subagent, and separately something around a `sofi doctor` run) rewrote ~85 of them mid-session
   (normalize-to-inline, then remove-entirely). Reverted each time; NOT recurring (confirmed: no hook,
   cron, git-filter, or settings file mutates agents — controlled test + code review of all 5 hooks +
   agentlint, which skips `tools:`). v7 fix: deliberately normalize ALL 105 to ONE canonical `tools:`
   form, reconciled against registry.yaml grants (Phase 6b). Until then, if `.claude/agents/*.md` show
   as modified with no intentional edit, `git checkout HEAD -- .claude/agents/` to restore. Do NOT
   commit a tools-block-removed state — it silently broadens tool grants.

## Phased plan & status
| # | Phase | Risk | Status |
|---|-------|------|--------|
| 1 | Foundation + kill real dead weight (engine/, orphan worktree, runtime junk, ignores) | 🟢 | ✅ DONE — commits 5a567a3, 5c90557, 65895f5 |
| 5a | CLAUDE.md honesty (hooks + CLI verbs) | 🟢 | ✅ DONE — commit ff233ba |
| 5b | registry.yaml drift: tool-grant fixes | 🟢 | ✅ DONE — arc-infra Write/Edit dropped to match spawnable (880da9d). gtw-router/conflict-resolver verified CONSISTENT (registry==spawnable==R/G/G), no change. |
| 5d | skills referencing mock/demo scripts as production | 🟡 | 🔶 PARTIAL — removed mock spec_review_preflight.py from sofi-spec-review active procedure (2563ddb). Full script deletion → see Dead-Prototype Purge below. Reflection confidence-gate wiring still ⏳. |
| DP | ~~Dead-Prototype Purge~~ **CANCELLED — premise was wrong** | ✅ | 🟢 CORRECTED — the audit's "zero callers" flag mislabeled working CLI tools as dead. These are **run** (`python3 <tool> <cmd>`), not imported, so zero import-callers is EXPECTED. Verified FUNCTIONAL: `ceo_toolkit.py routes` dumps the real 105-agent route table · `route.py`/`dispatch.py` print usage & work · `handoff_validator.py` runs and validates. DO NOT delete — they are the boardroom's documented manual toolkit. Genuine issues remaining (fix, don't delete): `agent_preflight.py` (broken `AGENT_BRIEFING.md` path) · `spec_review_preflight.py` (real mock — already removed from active skill 2563ddb; still listed in 18 docs as a tool, lower priority) · `squad_orchestrator_v2.py` (v5 test-harness main — verify before any action). **Lesson: test a CLI tool's functionality before ever calling it dead.** |
| 5c | gates.yaml state count 3→5; `sofi squad` hardcoded roster | 🟡 | ✅ DONE — state bar 3→5 (8335a74); `sofi squad` now sources roster from gates.yaml + revives `roles_for_gate` (c90a0b4). |
| 5e | agent_preflight.py broken briefing paths (v5 files) | 🟢 | ✅ DONE — repointed to live v6 doctrine, hydrates 3 files (7ee62f6). |
| 7-gap | lesson-vaccine loop — **CORRECTED: it WORKS** (3rd false-dead caught by testing, after ceo_toolkit + the `inherit` convention). `vaccine_for` reads LESSONS.md directly (org + project, both v5+v6 block dialects) — the SAME store `reflection_engine` writes to — and matched org lessons by keyword in test (3/1/2/3 hits for gate/squad/handoff/route topics; 0 for unrelated SAKK topics = correct). No wiring needed. What IS unused (95% of the module): the advanced managed-cache layer — `add_lesson`/`record_use`/`promote_candidates`/`select_for_injection` (confidence-decay + cross-project promotion). That is a **future feature**, not a bug — keep or trim later, no urgency. | ✅ | 🟢 verified working |
| 5d | skills referencing mock/demo scripts as production (spec_review_preflight.py mock; reflection confidence gate) | 🟡 | ⏳ |
| 4 | Purge v5 brain rot: `company/brain/org/{PERSONAS,TEAM_STATUS,HANDOFFS}.md` (30-agent/5-tier) | 🟢 | ✅ DONE — refreshed IN PLACE (architectural slots per BRAIN.md, NOT deleted → zero cascade), ~290 lines v5 rot removed, content now points to live sources; fc79731 |
| 3 | OODA engine (broken store() signature) + autopilot ("v2 live" but never ran) — retire + de-reference | 🟡 | ✅ DONE — deleted both + v5 docs + 2 stale reports + orphan branch; de-ref'd CLAUDE/MEMORY/reflection; commit f1702c6 |
| 6 | De-dup + dead functions | 🟡 | 🔶 PARTIAL — deleted dead budget.py + event_server.py (d8aeaaf). `_gate_num` dedup **SKIPPED**: gates.py (split) vs transitions.py (regex) are NOT identical → merging = behavior change, not safe dedup (behavior-preservation wins). runlog + index.html/identity.css token dedup deferred (low value / breakage risk). |
| 2 | Restructure `os/agents`→`os/toolkit/` + flatten tier nesting into `toolkit/gate/` | 🔴 | ✅ DONE — rename 90279c4, flatten f52b454 (runtime-verified: cli, scan/oracle clusters, uiux, dashboard, sofi CLI; 0 broken refs). `toolkit/ceo`→`core` also done (cd67ec5). Final toolkit/: `core · gate · uiux · devops · _TEMPLATE` (was 8 dirs incl 6 nested tier/role dirs). server-plane KEPT (live remote-publish subsystem, feeds Phase 8). |
| 6b | Deliberate spawnable frontmatter unification (canonical format for all 105 + reconcile grants with registry) — also fixes the `sofi doctor` write bug | 🟡 | ⏳ |
| 7 | Build the named-but-unbuilt room tools (kill-criterion-linter, two-track-classifier, token-dup linter, …) | build | ⏳ |
| 8 | ☁️ Cloud layer (Cloudflare + GitHub) | build | 🔶 PARTIAL — **GitHub CI ✅ live-green** (ca92820, pushed, runs on every push: YAML·imports·105-parity·secret-scan·junk). **Cloudflare dashboard ✅** (`dashboard/start.sh tunnel` via cloudflared, e8aeed4). Remaining: remote-agents = a Claude-Code harness capability, not framework code (needs concrete scope from owner) · oracle "strengthening" = vague (the desk already works) — pick a concrete improvement or close. Persistent Cloudflare named-tunnel/custom-domain needs owner's CF account token. |
| 9 | Final restructure + regenerate CLAUDE.md/ORG.md + docs + cutover + tag v7.0 | 🟡 | ⏳ |

## Rules for this program
- Every phase: commit (Conventional + Co-Authored-By trailer), then verify **read-only** (never `sofi doctor` until 5b/6b fixes it).
- v6 files are not physically removed until the very end (Phase 9 cutover), after v7 is proven.
- PAT revoked + branch pushed to origin (2026-07-08); GitHub Actions CI now gates every push.
- Update THIS file's status column at every phase close.
