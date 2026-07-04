# SOFI-AI Architectural Decisions & ADRs

## ADR-001: State-Hydration Boot Loop (Proven)
**Date:** 2026-06-15  
**Status:** ACTIVE  
**Decision:** Force `sofi sync <PRJ>` to read isolated git-backed `_context/` (STATE/CONTEXT/DECISIONS/HANDOFFS) before any agent executes.  
**Rationale:** Eliminates stateless amnesia; enables resumable multi-session work.  
**Outcome:** 60+ successful multi-session handoffs in PRJ-SAKK without context loss.

---

## ADR-002: Asymmetric Token Routing (routing.yaml v4.2)
**Date:** 2026-06-20  
**Status:** ACTIVE  
**Decision:** 80% haiku → 15% sonnet → 4% Fable → 1% Opus. Gatekeeper (Fable 5) hard-gates critical decisions (spec-review 7 steel rules).  
**Rationale:** Cost efficiency + quality preservation on arbitration.  
**Outcome:** Token burn ~60% lower than equivalent vanilla-agent approach.

---

## ADR-003: Blind Spot Filter (Context Reduction)
**Date:** 2026-06-22  
**Status:** SUPERSEDED (2026-07-03) — `lean-ctx` removed from the workspace  
**Decision:** Use `.claudeignore` for context window reduction.  
**Rationale:** Makes continuous local execution financially viable.  
**Outcome:** `.claudeignore` remains in use; the `lean-ctx` runtime was pulled out.

---

## ADR-004: 7 Steel Rules Spec-Review Gate
**Date:** 2026-06-25  
**Status:** ACTIVE  
**Decision:** /sofi-spec-review hard-gates (422-not-302, ApiException, /admin-in-503, unique-race, money-math, contract-parity, Tier-A ≥90%).  
**Rationale:** Catch money-safety + usability + security violations before merge.  
**Outcome:** Zero Tier-A regressions since implementation.

---

## ADR-005: Single Physical Projects Root + Per-Project Git Repos
**Date:** 2026-07-01  
**Status:** SUPERSEDED by ADR-008 (2026-07-03)  
**Decision:** Kill symlink at Lorka/projects. One real root ~/Desktop/projects/. Each PRJ-XXXX = own git repo + isolated brain (_context/).  
**Rationale:** Prevent cross-project bleed; clean git history per project.  
**Outcome:** Caddy docroots fixed (symlink→physical). Clear project isolation.

---

## ADR-006: SOFI-AI Architectural Hardening (Gemini Audit 2026-07-02)
**Date:** 2026-07-02  
**Status:** REMEDIATION IN PROGRESS  
**Decision:** Address 3 critical vulnerabilities identified in Gemini architectural audit:
1. **Semantic Drift Telephone Effect** → Triple-Contract Check in handoff protocol
2. **Port Collision & Environment Bleed** → Per-project port ranges + Caddy teardown + resource locks
3. **Fable-5 Lockout Loop** → Pre-flight Sonnet 5 classification + circuit breaker tuning

**Rationale:** Ensure multi-agent coordination remains bulletproof at scale. Prevent business logic loss across handoff chains. Isolate parallel squad execution.  
**Timeline:** 13 days (3 weeks parallel squads)  
**Phase 1:** Handoff integrity (Days 1–2)  
**Phase 2:** Resource isolation (Days 3–5)  
**Phase 3:** Gatekeeper hardening (Days 6–8)  
**Phase 4:** Exfiltration guard (Day 9)  
**Phase 5:** Observe loop (Days 10–11)  
**Phase 6:** Orchestration v2 (Days 12–13)  

**Success Metrics:**
- Handoff semantic drift incidents: 0 per 50 tickets (baseline: 2–3)
- Cross-project test failures: 0% (baseline: 15%)
- Spec-review arbitration loops (avg): 1.2 attempts (baseline: 3.1)
- Exfiltration incidents: 0 detected

**Owner:** CEO (Tier-0) + sofi-backend-tech-lead (Phase 2–3) + sofi-security-compliance-architect (Phase 4)  
**Dependencies:** None. All 6 phases can run in parallel (separate squads per phase).

---

## ADR-007: Gemini-Loop Teaching VII (4-Layer Enforcement)
**Date:** 2026-07-02  
**Status:** ACTIVE  
**Decision:** Autonomous Gemini loop with 4-layer runtime enforcement:
1. **Output Guard** (Critical) — Agent output interceptor validates no unsafe state mutations
2. **Circuit Breaker** (High) — Escalation on repeated failures
3. **Context Pruning** (Medium) — Strip sensitive data before external review desk push
4. **Pre-flight Hydration** (Operational) — Mandate state hydration before agent spawn

**Rationale:** Prevent runaway autonomous loops; enforce guardrails at runtime.  
**Outcome:** Teaching VII autonomous loop validated; safe for production.

---

## ADR-008: Projects Root Moved In-Repo (supersedes ADR-005)
**Date:** 2026-07-03  
**Status:** ACTIVE  
**Decision:** Moved physical projects root from `~/Desktop/projects/` to `~/Desktop/Lorka/projects/`, at explicit user request despite the 2026-07-01 incident that prompted ADR-005 (in-repo location broke every Caddy docroot). Each `PRJ-XXXX/` remains its own separate git repo, gitignored from Lorka's own history. Updated on the move: crontab (`PRJ-SAKK` schedule:run cwd), `.sofi-run/caddy/sites/{PRJ-SYRH,zanjour}.caddy` docroots (validated + reload pending manual `sudo systemctl reload caddy`, blocked for agents), and hardcoded literal-path fallbacks in `caddy_isolation.py`, `squad_orchestrator_v2.py`, `gemini-github-sync.py`, `observe_sentry_loop.py`, `ooda/engine/config.yaml`, `.claude/settings.local.json` that bypassed `sofi_tools.paths.projects_dir()`.  
**Rationale:** `paths.projects_dir()` already tolerates this (env override → `~/Desktop/projects` if present → in-repo fallback), so the *designed* resolution path was never actually broken — only the files hardcoding a literal string outside that function were. User-directed change; risk was disclosed and accepted.  
**Outcome:** pending — Caddy config validated but daemon reload requires manual sudo.

---

## ADR-009: SOFI v5.0 — The Integrity & Intelligence Layer
**Date:** 2026-07-03
**Status:** ACTIVE
**Decision:** Add a grounding + verification + self-improvement layer on top of the v4 structure, rather than rebuilding the structure. Six deep frontier-research sweeps (`.claude/docs/ai-guides/research/`: orchestration, context/memory, grounding, self-improvement, verification, spec-design — each cited to Anthropic engineering + arXiv 2025-2026) independently **validated v4's 5-tier/Advisor-gateway/gate-lifecycle/git-brain structure as correct** for a compliance-oriented gated SDLC, and flagged the alternatives (peer-to-peer mesh, vector-DB memory, 50-agent fan-out, trained verifier models) as over-engineering for SOFI's shape. So v5 is additive. Six components: **C1 Grounding** (`grounding.md` + universal-contract hooks + RCCF clause) — cite-or-abstain, execution-truth, verified-vs-inferred, conflict-surfacing; **C2 Reflection** (`reflection_engine.py` + `reflection.md` + `/sofi-reflect`) — scheduled "dreaming" distilling HANDOFFS→LESSONS.md, retain-by-default, never per-turn; **C3 Structured brain** (`tickets.py` query + `sofi brain-query` + memory-type frontmatter in `context-and-memory.md`); **C4 Verification** (`verification.md` + `gates.validate_evidence()` wired into `gate-check` + spec-review UNKNOWN verdict + `/sofi-secure` adversarial pass); **C5 Budgeted autonomy** (`routing.yaml` `effort_scaling`+`budgeted_autonomy` + verbatim-forwarding in handoff); **C6 RCCF v2** (clarify-before-commit, frozen brief, evidence block, effort class).
**Rationale:** The research verdict was consistent and cited: v4 got the org *structure* right; what it lacked was the integrity layer (agents couldn't be stopped from hallucinating unchecked or self-reporting success) and the intelligence layer (the org didn't learn from its own history). That's the genuine, grounded "radical development" — not a teardown of validated work.
**Outcome:** All new Python compiles; routing/registry YAML valid; `sofi doctor` PASS (30 agents unchanged); evidence-check + brain-query + reflection-engine dry-run all verified against real project data. Framework-only change — no project code touched, tier-isolation + git-discipline preserved. Design record: `.claude/docs/v5/SOFI-V5-ARCHITECTURE.md`.

---

## Future ADRs (Backlog)
- **ADR-010:** Sidecar observability (Sentry → DECISIONS.md feedback loop) — Gate 8 integration
- **ADR-011:** Parallel squad orchestration v2 — Dynamic resource binding + auto-cleanup
- **ADR-012:** Cross-project audit tooling — Automated compliance checks across all PRJ-* repos
