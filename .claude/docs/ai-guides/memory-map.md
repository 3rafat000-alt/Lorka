# Understanding Context Rot (Memory Map)

**Source:** https://www.aiwithmo.com/prompts/memory-map

## Summary
AI assistants on long-running projects experience "Context Rot" — the context window fills with irrelevant info, causing forgotten architectural decisions and broken working code. Fix: a `.memory` folder at the project root plus a `memory-map.md` index.

## Key Techniques / Patterns
- `.memory` folder stores architectural decisions, current-state docs, and bug logs (to prevent repeated mistakes).
- README as entry point — gives the AI immediate project-scope understanding before touching code.
- `memory-map.md` explicitly maps folder structure, DB relationships, component hierarchy.
- **Situation-based routing table**: task type → doc to read (e.g. "adding a UI component" → `ui-guidelines.md`, "modifying the database" → `schema-rules.md") — prevents random codebase browsing.

## Concrete Examples From the Article
The routing-table concept itself is the concrete deliverable — a lookup table mapping task categories to specific files.

## Relevance to SOFI
SOFI's `_context/` folder + `CLAUDE.md`'s "Boot" section already function as the `.memory`/README-entry-point pattern. What SOFI does **not** have explicitly: a **situation-based routing table** — right now agents infer which doc to read from their own spec + protocols, but there's no single lookup table like "adding a UI component → read X."

## Actionable Takeaway
Minor, optional improvement: a short routing table in `CLAUDE.md` or a new `engine/protocols/situation-routing.md` mapping common task types (new endpoint, schema change, UI component, deploy, incident) to the exact doc/protocol to consult first. Low priority — SOFI's per-role specs already do most of this implicitly via their "Context — read before acting" sections.
