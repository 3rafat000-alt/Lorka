# Breaking the Chains (Prompt Engineering & Agentic Workflows Guide)

**Source:** https://www.aiwithmo.com/prompts/improve-asking

## Summary
The article argues that most people underuse AI models by treating them as glorified search engines. It promotes a practical, no-fluff methodology built around structured prompting and agentic workflows to unlock real productivity gains. The author's core claim is that results depend far more on how the interaction is structured than on which platform is used.

## Key Techniques / Patterns
- Four-element prompt structure: **Role** (who the AI should act as) · **Context** (background info) · **Task** (specific ask) · **Format** (desired output shape) — essentially Role/Context/Task/Format.
- Agentic workflows over plain chat: chaining tools/steps instead of single back-and-forth Q&A.
- Combining specific tools in sequence for dev work (Claude Code, Lovable.dev, Supabase) as an example workflow stack.
- Constraint-based prompting: explicitly telling the model to skip theory/fluff and return only the finished, usable artifact.

## Concrete Examples From the Article
- A debugging prompt asking for a "complete, finalized code block ready to use" (no partial snippets or explanation).
- A SaaS architecture prompt requesting a database schema and API endpoints returned as a table.
- A reusable template with placeholders for role, task, context, and output format.

## Relevance to SOFI
Directly applicable. The article's four-element structure (Role · Context · Task · Format) is essentially SOFI's existing **RCCF** delegation protocol (Role · Context · Command · Format) — this is independent external validation that the pattern is sound, not a new idea to adopt. The "constraint-based prompting" habit (demand finished artifacts, no fluff) reinforces SOFI's "big brain small mouth" doctrine and the instruction that code/commits/security must stay in normal (uncompressed) prose while everything else stays terse.

## Actionable Takeaway
None — the technique (RCCF-equivalent structured prompting) is already implemented in SOFI via `engine/protocols/01-delegation-rccf.md`; treat this article as confirming evidence rather than a new change to make.
