# Claude Fable 5 Is Here: The Mythos-Class Model, Made Safe for Everyone

**Source:** https://www.aiwithmo.com/prompts/claude-fable-5-release

## Summary
Anthropic released Claude Fable 5 on June 9, 2026 — the first public model from the new "Mythos-class" tier, built by safety-wrapping an internal model (Mythos) that was too capable at finding cybersecurity vulnerabilities to release unrestricted. Fable 5 tops SWE-Bench Pro (80.3%), Terminal-Bench 2.1, and GDPval-AA, beating Opus 4.8, GPT-5.5, and Gemini 3.1 Pro, at $10/$50 per million input/output tokens.

## Key Techniques / Patterns
- **Classifier-based fallback routing**: instead of refusing sensitive requests (cybersecurity, bio/chem, model-distillation topics), Fable 5 silently reroutes them to Opus 4.8 rather than declining outright.
- **Transparent routing notification**: the user is told when a query was rerouted, preserving trust instead of a silent swap or a hard refusal.
- **Conservative-tuning tradeoff**: over-catches (routes away) some harmless requests (under 5% of sessions) to minimize the risk of missing a genuinely unsafe one — an explicit precision/recall tradeoff choice.
- **Task-fit guidance**: vendor explicitly recommends the frontier model only for long/complex/high-value tasks (big migrations, deep research), and a cheaper model for quick/routine work.

## Concrete Examples From the Article
- Stripe: migrated a 50-million-line Ruby codebase in one day (vs. ~2 months manually).
- SWE-Bench Pro: Fable 5 80.3% vs. Opus 4.8 69.2%, GPT-5.5 58.6%, Gemini 3.1 Pro 54.2%.
- Vision: rebuilt web app source from screenshots; beat Pokémon FireRed from raw screenshots, no tools.
- Safety reroute rate: under 5% of sessions trigger fallback to Opus 4.8.

## Relevance to SOFI
Mostly a product/pricing announcement about a model SOFI's own routing ladder already names (🔮 `fable` — gatekeeper tier in `engine/routing/routing.yaml`), so it's useful as capability/cost reference. One technique is transferable: **transparent fallback routing** — when a request gets escalated to a different model tier, tell the requester why, rather than silently swapping. SOFI's routing already asks agents to "log route in thinking," but this article's pattern argues for surfacing the *reason* for an escalation (not just the route taken), which is a small refinement, not a new capability.

## Actionable Takeaway
When `sofi route` escalates a task up the ladder (e.g., sonnet → fable), have the routing log include the *trigger evidence* for the escalation, not just the destination tier — mirrors Fable 5's "notify user why this was rerouted" pattern and keeps routing decisions auditable in the brain.
