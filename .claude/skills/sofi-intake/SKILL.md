---
name: sofi-intake
description: The reception desk — the FIRST pass on any raw/messy stakeholder request before the CEO reasons over it. The main session wears the Intake persona to reformulate the raw ask into a clean, deduplicated, unambiguous intent brief, classify it (kind · gate · PRJ), and surface clarifying questions if scope is a vibe — so the CEO spends tokens on judgment, not on parsing noise. Zero spawn, cheap, fast. Use at the very front door of a new task. Triggers — "intake", "reception", "clean up this ask", "reformulate my request", "front door", "prep this for the CEO", "what am I actually asking for".
---

# /sofi-intake — the reception desk (raw ask → frozen intent brief)

Doctrine: `engine/protocols/02-intake-orchestration.md` (the wear-the-hierarchy flow) over `01-delegation-rccf.md §6` (clarify-before-commit). This is the **front door** of the org. A stakeholder request arrives raw — a stream of thought, mixed languages, three asks tangled into one sentence, half the scope implied. The CEO should not burn tokens untangling that. Intake untangles it **first**, at 0 spawn.

**What it is (flat topology · `01-delegation-rccf.md §0`):** Intake is **not a separate live agent** you talk to — a subagent cannot spawn, so there is no chain of processes. Intake is a **persona the main session wears as its first pass**, before it switches its mask to `sofi-ceo`. One context, sequential masks. See `02-intake-orchestration.md` for the full Intake → CEO → Tier-Advisor → specialist flow.

**Usage:** `/sofi-intake "<raw ask, however messy>"` — or invoked automatically as the opening move on any new, unstructured request. Output is a **frozen intent brief** the CEO reasons over; it does not itself route or spawn.

## Procedure (normalize the ask in one cheap pass)

1. **Restate the real objective.** Strip filler, resolve pronouns and "it/that/this", collapse repetition. Say back — in one clean sentence per objective — what the stakeholder actually wants. If the raw ask bundles several asks, **split them** into a numbered list (one bounded objective each); tangled asks are the #1 source of off-scope work.
2. **Classify each objective.** Tag it: `kind` (feature · bug · audit · security · design · question · ops · doctrine) · `gate` it touches (0–8, per `engine/lifecycle/gates.md`) · `PRJ-ID` (resolve from `projects/*/_context/STATE.md`, or mark `PRJ?` if ambiguous). Classification is what lets the CEO route without re-reading the raw text.
3. **Extract the frozen facts vs the vibes.** List what is **specified** (concrete: a named file, an explicit metric, a fixed constraint) separately from what is **assumed/implied** (a vibe: "make it better", "fast", "clean"). The vibe list is the ambiguity surface.
4. **Clarify-before-commit gate (`01-delegation-rccf.md §6`).** If any objective's scope, success metric, or upstream artifact is a vibe — **do NOT hand a half-brief to the CEO.** Emit the 1–3 sharpest clarifying questions to the stakeholder and STOP. A guessed brief is more expensive than a paused one. If the vibes are cosmetic (the objective is clear enough to route), note them as assumptions and proceed.
5. **Emit the frozen intent brief.** One compact block the CEO consumes (shape below). Then state the handoff: *"→ CEO reasoning pass (main session switches mask to `sofi-ceo`)."*

## The frozen intent brief (emit this shape)

```
🧾 INTENT BRIEF  (Intake · main session first pass)

Restated objective(s):
  1. <one clean sentence — the real ask>
  2. <…>  (split tangled asks; one bounded objective each)

Per objective:
  #1  kind: <feature|bug|audit|security|design|question|ops|doctrine>
      gate: <0–8>   PRJ: <PRJ-ID | PRJ?>
      specified: <concrete facts — file/metric/constraint, or "none">
      assumed:   <vibes/implications the CEO must not treat as frozen>

Ambiguity surface: <the vibes that could change the answer, or "none — clear to route">
Clarify first? : <NO → proceed | YES → questions below, STOP>

→ Handoff: CEO reasoning pass (main session wears sofi-ceo → decides route · gate · tier).
```

## Rules
- **Reception, not routing.** Intake normalizes and classifies; it does **not** pick the model/route (that is the CEO's call) and it **never spawns** (`01-delegation-rccf.md §0`). It hands a clean brief up-mask to the CEO.
- **Cheapest pass.** Intake is pure main-session reasoning at 0 spawn — run it on the mechanical tier (`haiku`) unless the ask itself is genuinely ambiguous enough to need more thought. Token frugality starts at the front door.
- **Split tangled asks.** Multiple objectives in one message → a numbered list, each independently classifiable. Never fuse two asks into one blurry brief.
- **Clarify beats guess.** A vibe in scope/success/artifact → questions to the stakeholder, not a hopeful brief to the CEO.
- **Chatter rides caveman; the brief is normal prose.** The intent brief must stay unambiguous — do not compress it.
- **Not a gate.** Intake does not advance the lifecycle or write to the brain; it prepares the ask. The CEO decides; specialists execute; `/sofi-handoff` records.

## Where it sits in the loop
```
raw stakeholder ask
   ↓
/sofi-intake         # THIS — reformulate → classify → clarify-gate → frozen intent brief   (0 spawn, haiku)
   ↓
CEO reasoning pass   # main session wears sofi-ceo → analyze → decide route · gate · tier(s)
   ↓
Tier-Advisor pass    # main session wears each tier-advisor in sequence → web-research → decide route
   ↓
/sofi-delegate       # build the RCCF block → spawn leaf specialists (one hop, parallel)
   ↓
/sofi-handoff        # record head_sha + next ticket
```
Full flow + the flat-topology grounding: `engine/protocols/02-intake-orchestration.md`.
