# Playbook — Gate 3 Architecture

> Owner: `arc-lead` (drafting: `arc-system-architect`, `arc-data-architect`, `arc-api-architect`, `arc-integration-architect`, `arc-infra-architect`; squad partners `dat-lead` and `sec-lead` in `08-data`/`09-security`). The room's core recurring procedure — frozen prototype → stack + schema + contract + integrations + infra + traceability matrix → signed Gate-3 exit bundle, run as the lead of a three-room squad behind one frozen input.

## When to run this

Every time `03-design` tags Gate 2 (`<PRJ>-gate2-done`) and `Prototype_Spec.md` + `Content_Strings.json` are frozen — the trigger for every project's Gate-3 pass.

## Steps

### 1. Orient — never act on memory
```bash
sofi sync PRJ-XXXX
git -C projects/PRJ-XXXX log --oneline -8
```
Read, in order: `projects/PRJ-XXXX/_context/STATE.md` (branch + `head_sha`) → `HANDOFFS.md` (the open Gate-3 ticket) → `CONTEXT.md`. Confirm `head_sha` matches the tree's HEAD before touching anything.

### 2. Confirm Gate 2 actually closed
```bash
sofi gate-check PRJ-XXXX --gate 2
```
If this fails: **reject upward** to `dsn-lead` with the specific missing artifact named (usually an incomplete `Prototype_Spec.md` or a `Content_Strings.json` still carrying invented copy), stop. Do not architect against an unfrozen prototype (Teaching II).

### 3. Fan out the three-room squad behind the frozen prototype
```bash
sofi squad PRJ-XXXX 3
```
Renders the concurrent Work Orders for `04-architecture`, `08-data`, `09-security` — all three rooms read the *same* frozen `Prototype_Spec.md` + `Content_Strings.json`, none waits on another room's output to start (`effort_scaling.cross-room`). Claim shared paths first if the project has an existing `docs/` tree with conflicting file names:
```bash
sofi claim PRJ-XXXX docs/PRJ-XXXX_Schema.sql --agent arc-data-architect
```

### 4. `arc-lead` dispatches `arc-system-architect` first
```bash
sofi dispatch PRJ-XXXX --agent arc-system-architect
```
Everything else in the room leans on the stack choice — `docs/PRJ-XXXX_Tech_Stack.md`, the FossFLOW component diagram, and the screen→component→endpoint traceability matrix (built incrementally; the endpoint column fills in once step 6 lands). If a screen genuinely resolves to no plausible component, `arc-lead` rejects that feature to Backlog here — never invents a component to cover the gap.

### 5. Fan out schema, contract, and integrations in parallel behind the frozen stack
```bash
sofi dispatch PRJ-XXXX --agent arc-data-architect       # schema + ER + migration design
sofi dispatch PRJ-XXXX --agent arc-integration-architect  # 3rd-party plans, runs independently
```
`arc-api-architect` runs slightly behind `arc-data-architect` — the contract reuses the schema's entities, so dispatch it once the schema draft lands:
```bash
sofi dispatch PRJ-XXXX --agent arc-api-architect
```
`arc-integration-architect` coordinates directly with `arc-api-architect` on webhook-shape alignment — both report through `arc-lead`, but the coordination itself is a same-room exchange, not a separate escalation.

### 6. `arc-infra-architect` drafts the topology once the stack is stable
```bash
sofi dispatch PRJ-XXXX --agent arc-infra-architect
```
Reads the frozen stack and (once it lands from the `09-security` squad partner) the signed `Threat_Model.md`. His output is a design handed to `arc-lead`, not a committed file — `arc-lead` writes `docs/PRJ-XXXX_Infra_Topology.md` from it as the explicitly-named "infra" piece of assembling the bundle.

### 7. `arc-lead` gate-checks every draft
For each specialist's artifact: does it cite `file:line` back to the frozen prototype or the upstream artifact it derives from? Does the traceability matrix have zero orphan components and zero untraced screens? Does every migration carry a passing `migration_check.py` result? Does every third-party field cite a fetched, dated vendor source? Does the infra design name and budget every deliberate trade-off? One rejection round per gap, named specifically — never a vague "needs work."

### 8. Confirm the squad partners' artifacts landed
```bash
sofi gate-check PRJ-XXXX --gate 3 --room 08-data
sofi gate-check PRJ-XXXX --gate 3 --room 09-security
```
`arc-lead` will not freeze the bundle without the signed `Threat_Model.md` from `sec-lead` (no unmitigated High risk) and, when personal data is touched, the `PII_Map.md` from `dat-privacy-officer`. A missing or unsigned threat model blocks the freeze outright — this is not a soft dependency.

### 9. Assemble the Gate-3 bundle
`arc-lead` assembles the frozen bundle: `docs/PRJ-XXXX_Tech_Stack.md` + `docs/PRJ-XXXX_Schema.sql`/ERD + `docs/PRJ-XXXX_OpenAPI.yaml` + `docs/PRJ-XXXX_Integration_Plans.md` + `docs/PRJ-XXXX_Infra_Topology.md` (written by him from Kenji's design) + the completed traceability matrix + the signed `Threat_Model.md` forwarded from `sec-lead`.

### 10. Mechanical gate-check
```bash
sofi gate-check PRJ-XXXX --gate 3
```
Confirms: all bundle artifacts exist with evidence blocks; traceability matrix complete; every migration reversible; threat model signed with no unmitigated High risk. Fails → the specific missing artifact is filed as a blocker in `HANDOFFS.md`, gate stays at 3.

### 11. Adversarial verify (never self-graded)
```bash
sofi dispatch PRJ-XXXX --agent gtw-gatekeeper --gate 3
```
`gtw-gatekeeper` sees only the bundle + the ORIGINAL Gate-3 exit bar (`company/nexus/gates.yaml`) — never `arc-lead`'s own reasoning. PASS/FAIL/UNKNOWN; UNKNOWN escalates, it never defaults to PASS.

### 12. Record + tag + hand off
```bash
sofi checkpoint PRJ-XXXX "feat(architecture): freeze Gate-3 bundle — stack, schema, contract, integrations, infra, traceability"
sofi gate-tag PRJ-XXXX 3
```
Append `CONTEXT.md` (+ `DECISIONS.md` for every irreversible stack/provider call), update `STATE.md` `head_sha`, and write the next tickets in `HANDOFFS.md` addressed to `bck-lead`, `fnt-lead`, `mob-lead`, and `dat-lead` for Gate 4. Report the Gate-3 status to `brd-ceo`/`brd-cto`. `/sofi-handoff` runs this whole step.

## Self-check before closing the gate

1. Does every screen in the frozen prototype trace to a component and an endpoint, and does every component trace back to a screen?
2. Does every migration design carry a `migration_check.py`-clean rollback?
3. Does every third-party field in `Integration_Plans.md` cite a fetched, dated vendor source — none guessed?
4. Is the signed `Threat_Model.md` in hand with no unmitigated High risk?
5. Was the mechanical gate-check AND the `gtw-gatekeeper` adversarial verdict both run — never one substituting for the other?

## Rules

- No specialist inside the room reaches `bck-lead`/`fnt-lead`/`mob-lead`/`dat-lead`/`sec-lead` directly — everything routes through `arc-lead`.
- The three-room squad (`04-architecture`/`08-data`/`09-security`) fans out only because all three read the *same* frozen prototype independently — never fan out sequential phases of one ticket.
- `arc-lead` never freezes the bundle around an open security gap, regardless of schedule pressure — the threat model's signature is a hard gate, not a formality.
- Pairs with `/sofi-gate` (wraps steps 10-11) and `/sofi-handoff` (wraps step 12).
