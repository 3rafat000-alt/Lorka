# 🎮 SOFI AI — Client Guide (how to ask the team)

Your guide to running the agent enterprise with the best context and the fewest tokens. Read it once, then use `COMMANDS.md` as a quick card.

> Golden rule: **Talk to the CEO (Magnus / `sofi-ceo`), not the individuals.** He routes, picks the agent, injects the context. You give the goal — he runs the company.

---

## 1. How to start (3 steps)

### Step 1 — Boot the brain
Paste `SOFI_SYSTEM_PROMPT.md` as the system prompt of a new project. Or, in Claude Code:
```
Use the sofi-ceo agent
```

### Step 2 — Give an idea
```
New project: <your idea in one sentence>. Start onboarding.
```
The CEO creates `PRJ-XXXX`, prepares the brain, and asks you **5 deep questions**. Answer them → the cascade runs.

### Step 3 — Let the team work
Each gate produces files under `projects/PRJ-XXXX/`. You review and decide whether to continue.

---

## 2. The professional request format (copy and fill)

The closer your request is to this shape, the better the context and the sharper the result:

```
Goal:     <what you want, in one sentence>
Project:  PRJ-XXXX        (or "new")
Gate:     <if you know it; otherwise leave it to the CEO>
Limits:   <budget / platform / stack / deadline>
Priority: CRITICAL | HIGH | MEDIUM | LOW
Success:  <when you'll call it done>
```

**Good example:**
```
Goal: Add fingerprint login to the app.
Project: PRJ-0001. Priority: HIGH.
Limits: Flutter, must work offline.
Success: User logs in by fingerprint, PIN fallback, covered by tests.
```

**Bad example (wastes tokens):** "Make me a nice app." ← vague; the CEO will ask 5 questions before any work.

---

## 3. Core commands

| You want… | Tell the CEO |
|-----------|--------------|
| New project | `New project: <idea>. Start onboarding` |
| Advance to the next gate | `continue` |
| Run through without pausing | `assume reasonable answers and proceed to gate <n>` |
| Know where we are | `where are we?` (reads `STATE.md`) |
| Activate a specific agent | `Use the sofi-<role> agent` |
| Review code/a branch | `review <file/branch>` → activates cavecrew-reviewer |
| Locate code | `where is <X> defined?` → cavecrew-investigator |
| Stop compressed mode | `normal mode` |
| Save tokens | `/caveman ultra` |

---

## 4. Calling agents by name (when to bypass the CEO)

Usually **don't call individuals** — the CEO knows the sequence. But if you want a specialist directly:

```
Use the sofi-<role> agent: <task>
```

| Role | Name | Use for |
|------|------|---------|
| `sofi-ceo` | Magnus Holt | **default — everything** |
| `sofi-chief-product-strategist` | Amara | problem definition, scope, questions |
| `sofi-ux-researcher` | Hiroshi | personas, user research |
| `sofi-journey-architect` | Sofia | journey map |
| `sofi-ui-ux-designer` | Dan | prototypes, screens, a11y |
| `sofi-content-strategist` | Peg | UI copy |
| `sofi-principal-system-architect` | Vikram | stack, architecture |
| `sofi-data-schema-engineer` | Elena | database, migrations |
| `sofi-api-integration-specialist` | Marco | OpenAPI, integration |
| `sofi-security-compliance-architect` | Ruth | security, threat model |
| `sofi-database-engineer` | Günther | database, query optimization |
| `sofi-api-engineer` | Priya | APIs, jobs, queues, integration |
| `sofi-backend-blade-engineer` | Aisha | backend + Blade views (full ownership) |
| `sofi-frontend-react-engineer` | Grace | React/CSS/JS, styling + accessibility |
| `sofi-mobile-engineer` | João | mobile — Flutter (full ownership) |
| `sofi-tier-2-advisor` | Elif | cross-tier gateway for Development work |
| `sofi-qa-sre-lead` | Barb | quality gate |
| `sofi-automated-testing-engineer` | Kwame | automated tests |
| `sofi-manual-exploratory-tester` | Rosa | exploratory testing |
| `sofi-performance-load-analyst` | Ahmed | load + performance |
| `sofi-devops-cloud-lead` | Linda | deployment |
| `sofi-cicd-pipeline-engineer` | Tomás | CI/CD pipelines |
| `sofi-observability-sre` | Naomi | monitoring + SLO |

> Full roster with personas in `engine/PERSONAS.md`.

---

## 5. The nine gates (what each `continue` does)

```
0 Inception    → Amara: problem + 5 questions
1 Discovery    → Hiroshi + Sofia: personas + journey
2 Design       → Dan + Peg: prototypes + copy
3 Architecture → Vikram + Elena + Marco + Ruth: stack + DB + API + security
4 Build        → 3 parallel squads: Backend + Frontend + Mobile
5 Quality      → Barb: tests + design audit → sign-off
6-7 Deploy     → Linda: staging + UAT + Blue/Green
8 Observe      → Naomi: SLO + alerts → loop back to gate 1 on any breach
```
Never skip a gate. Each gate needs the previous one's sign-off.

---

## 6. Token-saving commands (Caveman)

| Command | Effect |
|---------|--------|
| `/caveman lite` | drop filler only (for research/design) |
| `/caveman full` | default mode (~65% saving) |
| `/caveman ultra` | telegraphic (for high-volume code) |
| `normal mode` / `stop caveman` | turn off compression |
| `/caveman-stats` | how many tokens you saved |

**Code, security, and commits are always written normally — never compressed.**

---

## 7. Best practices (best context, fewest tokens)

✅ **Do:**
- Talk to `sofi-ceo`; leave the routing to him.
- Give a goal + limits + success definition (format in §2).
- Ask `where are we?` before any big request — it reads the brain instead of re-explaining.
- One project = one `PRJ`. Don't mix.
- If answers are known, say `assume and continue` — it runs without pausing.

❌ **Don't:**
- No vague requests ("make something nice") — they waste tokens on questions.
- Don't skip gates manually — it breaks traceability.
- Don't mix two projects in one request — isolation breaks.
- Don't ask a developer for an architectural decision — that's the CEO/architect's job.

---

## 8. Where to find everything

| You want | File |
|----------|------|
| The constitution | `SOFI_SYSTEM_PROMPT.md` |
| The team as humans | `engine/PERSONAS.md` |
| Who does what | `engine/ROSTER.md` |
| How the CEO runs it | `engine/RUNBOOK.md` |
| Cost per task | `engine/routing/routing.yaml` |
| Shared working methods | `engine/protocols/` |
| The script layer | `engine/tooling/README.md` + `engine/tooling/GOVERNANCE.md` |
| Your project's live state | `projects/PRJ-XXXX/_context/STATE.md` |
| Quick shortcuts | `COMMANDS.md` |

---

*Start now: `New project: <your idea>. Start onboarding`*
