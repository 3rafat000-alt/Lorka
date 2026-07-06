# 🧭 Coordination & the Registry — killing context amnesia (binding)

> **Foundation:** serves Teaching **II (Hierarchical Flow)**, **IV (Token Economy)**, and **V
> (Continuous Metamorphosis)**. Read `engine/DOCTRINE.md`, then `01-delegation-rccf.md` (how you hand
> off) and `02-intake-orchestration.md` (the mask flow) — this file is the third leg: **how the team
> stays coordinated across spawns without re-reading the world each time.**

**Context amnesia** = every spawned agent starts blind, re-reads the whole brain to orient, and the
main session re-reads each raw artifact to know what happened. At SOFI's current scale that is fatal:
the active project's `HANDOFFS.md` is **154 KB**, `STATE.md` **43 KB**, `CONTEXT.md` **45 KB**.
Telling every leaf to "read STATE → HANDOFFS → CONTEXT" bills **~240 KB per spawn** — pure
re-derivation. Ten leaves = 2.4 MB of tokens spent locating, zero spent judging. That is the drain
this protocol closes.

The fix is four moves, all pointing the same way — *the brain layer reads once and hands down a
distilled slice; the leaves execute on the slice and hand back a fixed receipt; a compact **registry**
lets the brain layer know "what exists" without re-opening a single artifact.*

---

## §1. Two context classes — who reads what (the read/execute split · binding)

Every byte an agent could read falls into exactly one of two classes. **This is the load-bearing
rule of this protocol.**

| Class | Files | Who may read it | Why |
|-------|-------|-----------------|-----|
| **Coordination context** (the brain) | `STATE.md` · `CONTEXT.md` · `DECISIONS.md` · `HANDOFFS.md` · `REGISTRY.md` · `LESSONS.md` | **Brain layer ONLY** — the main session while wearing the **CEO** or a **tier-advisor** mask | Huge, history-heavy, changes every step. Reading it is the act of *deciding + delegating*, not *building*. |
| **Work context** | the **one frozen upstream artifact** (spec / OpenAPI / schema / prototype) + the exact **`file:line` set the Python locator returned** + the code files the task edits | **Leaf specialists** (handed to them inside the RCCF) | Small, stable, task-scoped. This is the material of *building*. |

**The rule, one line:** *the CEO + the 5 advisors read, decide, and delegate; the leaf specialists
go straight to execution on a frozen slice and never open the brain.* (This is the user's mandate and
the article's "only the main agent reads the coordination docs.")

**Consequences:**
- A leaf's RCCF **Context** field carries a **distilled brain slice** — the ≤5 binding facts/decisions
  the mask lifted out of the brain — **not** a pointer to STATE/CONTEXT/HANDOFFS. The leaf never
  greps 240 KB; the mask already holds it in the main session's live context and pastes only what
  binds *this* task. (This refines `01-delegation-rccf.md §2` "Context": **point at the frozen
  artifact; distill the brain.**)
- The brain layer reads the brain **once** — it is already resident in the main session across the
  Reception → CEO → advisor masks (`02-intake-orchestration.md`). No mask re-reads what the prior
  mask already loaded.
- The old "Read order (every agent)" in `context-and-memory.md` is now the **read order of the brain
  layer**. Leaves have a different, tiny read order: *the frozen artifact + the located `file:line`,
  nothing else.*

---

## §2. The Registry — the anti-amnesia index (`_context/REGISTRY.md`)

A compact, append-only, **one-line-per-deliverable** index the brain layer scans to answer *"what
already exists, is it done, where does it live, what proves it"* **without re-opening the artifact or
re-reading HANDOFFS.** It is to produced work what `MEMORY.md` (root) is to doctrine: a routing map,
pointers only.

**Location:** `projects/<PRJ-ID>/_context/REGISTRY.md` — one per project, isolated by `PRJ-ID`
(Teaching III), lives beside the rest of the brain.

**Format** (pipe-delimited, newest first — greppable, and appendable at 0 model tokens by the tool):
```
# REGISTRY — PRJ-XXXX   (artifact index · brain-layer read only · append via registry.py)
# fmt: TKT | gate | agent | status | artifact-path | sha | Δbytes | headline
TKT-0042 | g4 | backend-blade-engineer | DONE     | app/Http/Controllers/API/AuthController.php | b0dbb45 | +214 | POST /auth/login end-to-end, matches OpenAPI
TKT-0041 | g4 | data-schema-engineer   | DONE     | database/migrations/2026_07_06_wallets.php  | a1c9f30 | +88  | wallets + ledger, reversible
TKT-0043 | g5 | security-pen-tester    | BLOCKED  | projects/PRJ-SAKK/_context/reports/idor.md   | —       | —    | IDOR on /wallets/{id}; needs schema authz fix
```

**Read/write rules (binding):**
- **Read:** brain layer only. Before spawning, the mask scans REGISTRY (one screen) to see what's
  already built, done, or blocked — instead of re-reading 154 KB of HANDOFFS. Leaves **never** read
  it.
- **Write:** appended by the main session at the **VERIFY + RECORD** step (`02-intake-orchestration.md
  §2`), mechanically, from the leaf's `registry:` line (see §3). Use the tool, not hand-editing:
  `python3 engine/tooling/agents/ceo/registry.py add …`.
- **One line, ever.** A deliverable is one row. Re-work updates the row's `status`/`sha` in place, it
  does not add a second row. The prose detail still lives in HANDOFFS (episodic) — REGISTRY only
  *indexes* it.
- **Not a replacement for the brain** — it is the **index over** it. HANDOFFS keeps the full episode;
  DECISIONS keeps the ADRs; REGISTRY is the fast lookup so the brain layer rarely has to open either.

---

## §3. The result header — how a leaf hands back so the brain never re-reads the raw work

Every leaf specialist ends its return with this fixed block (and only this block is what the main
session consumes to synthesize + update the registry). Standardizing the *shape* is what lets the
brain layer parse a result in one glance instead of re-reading the whole artifact — the article's
"output standardization."

```
✳ RESULT — <agent> · <ticket> · gate <n>
status:   DONE | BLOCKED | ESCALATE
artifact: <exact path>   (Δ +N/-M lines, sha <short>)
evidence: <command> → exit 0        |   <file:line> proof        (verification.md V1 — no bare "done")
registry: TKT-#### | g<n> | <agent> | <STATUS> | <path> | <sha> | +Δ | <one-line headline>
handoff:  <next agent, or "none">
```

The `registry:` field is pre-formatted **by the leaf** to the §2 line shape, so the main session's
record step is a mechanical copy — `registry.py add "<that line>"` — never an authoring step. The raw
artifact is opened by the brain layer **only to make a decision**, never to check *whether* the work
happened (that's §4).

---

## §4. Verify without reading (mechanical gate before any judgment)

The main session confirms a leaf's deliverable **with Python/bash, not by reading the artifact.**
Reading is reserved for synthesizing a *decision*; existence and correctness are checked mechanically
(the article's "verification via bash — existence, size, word count").

Ladder, cheapest first:
1. **Existence + shape:** `python3 engine/tooling/agents/ceo/registry.py verify <path>` → prints
   `exists · bytes · words · sha` (or a `MISSING` non-zero exit). Cross-check the `Δ`/`sha` against
   the leaf's `✳ RESULT` header — a mismatch means the leaf lied or half-finished.
2. **Mechanical gate:** `python3 engine/tooling/agents/ceo/sofi_verify.py --prj <PRJ> --md` — exit 0
   gates the pipeline (`php -l` · `view:cache` · `route:list` · `flutter analyze`). Self-report is
   never evidence (`verification.md` V1).
3. **Adversarial accept:** only *after* 1–2 pass, a fresh-context check of the deliverable against the
   **original ticket criteria** (`verification.md` V2) — the receiver grades, never the implementer.

Only if all three pass does the main session open the artifact — and then to *decide the next move*,
not to verify the last one.

---

## §5. Re-delegation — putting the SAME agent back on a task

You do not need a new persona for every unit of work. The same specialist can be handed the next
unit two ways — **both one hop from the main session, neither ever nested** (`01-delegation-rccf.md
§0`):

| Mechanism | When | Cost | How |
|-----------|------|------|-----|
| **Continue** (`SendMessage`) | the agent is **still alive** *and* the **same frozen context still holds** (tight iterate loop: build → its own test fails → fix) | cheapest — context intact, **zero re-brief** | `SendMessage` to that agent's id/name with the next bounded unit. It resumes with full memory of round 1. |
| **Re-spawn** (new round) | the agent **closed**, *or* the **frozen context changed** (round-1 returns reshaped the work) | one fresh RCCF | spawn the **same `agentType`** again with a new frozen RCCF block. No memory of round 1 — **the main session carries the bridge** (prior result → new Context slice). |

**Rules (binding):**
- **Same context + alive → continue. Changed context or closed → re-spawn.** Don't re-spawn what you
  can continue (wastes a re-brief); don't continue across a changed frozen artifact (that's stale
  context rot).
- A continuation is a **new bounded unit**, *not* a live correction dripped into a frozen brief — the
  no-instruction-drip freeze (`01-delegation-rccf.md §6`) still holds. If the *original brief* was
  wrong, stop and re-spawn clean; if it was right and there's simply a *next* step, continue.
- Re-delegation is still **flat**: continue/re-spawn is always the **main session** talking to a leaf.
  A leaf never re-delegates to itself or anyone else.
- Log which you chose and why in `<thinking>` (Teaching IV) — a continue that should have been a
  re-spawn silently carries stale context.

---

## §6. The loop, with coordination wired in

```
orient (sofi sync)                         ← brain layer reads brain ONCE
  → scan (sofi_scan.py, 0 tokens)          ← Python locates file:line
  → check REGISTRY (one screen)            ← "what already exists?" — no re-reading artifacts
  → distill slice → build RCCF             ← paste binding facts, NOT brain pointers
  → spawn leaf / continue (SendMessage)    ← execution: work-context only
  → leaf returns ✳ RESULT header           ← fixed shape, parse-in-a-glance
  → verify WITHOUT reading (registry.py verify · sofi_verify.py)
  → record: registry.py add + checkpoint   ← REGISTRY row + git SHA
  → next ticket / next round
```

---

## §7. Grounding

- Read/execute split & "only main reads coordination docs": the article's mechanism, adopted here as
  §1; enforced by the RCCF Context refinement (`01-delegation-rccf.md §2`).
- Flat topology / one-hop / no nested spawn (why re-delegation is still main→leaf):
  `01-delegation-rccf.md §0`.
- Mask flow & the VERIFY + RECORD step that writes the registry: `02-intake-orchestration.md §2`.
- Brain layout, memory types, and the (now brain-layer) read order: `context-and-memory.md`.
- Evidence-over-self-report and fresh-context accept: `verification.md` V1/V2.
- Tool: `engine/tooling/agents/ceo/registry.py` (`add` · `list` · `find` · `verify` · `prune`) —
  0-model-token registry ops, mirrors the `sofi_scan.py` / `sofi_verify.py` standalone pattern.

**The doctrine in one line:** *the brain layer reads the world once and hands down a slice; the leaves
build the slice and hand back a receipt; the registry remembers what exists so no one ever re-reads
the world to find out.* 🪨
