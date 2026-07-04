# Grounding Rules and Instructions Files for AI Agents

**Source:** https://www.aiwithmo.com/prompts/grounding-rules-instructions-file

## Summary
AI models default to fabricating confident-sounding but false answers when they lack information — more dangerous than admitting ignorance. Agent-mode tools (Claude Cowork, ChatGPT Codex, Gemini Antigravity) read an instructions file before every response (`CLAUDE.md`/`AGENTS.md`/`GEMINI.md`) — "it is not permitted to answer your question before it has read that instructions file."

## Key Techniques / Patterns
Six grounding rules: (1) Source of Truth — answer only from folder contents, files override general knowledge; (2) Honesty — state plainly when info isn't available (called the most critical rule); (3) No Fabrication — never invent numbers/dates/names/citations; (4) Citation — every claim needs file attribution; (5) Knowledge Separation — label non-grounded general knowledge explicitly; (6) Conflict Resolution — show disagreeing sources rather than silently picking one.

## Concrete Examples From the Article
Test grounding by asking a question outside the files' scope — a properly grounded agent answers "I do not know."

## Relevance to SOFI
**Genuine gap.** SOFI's `engine/protocols/00-operating-system.md` (the universal agent contract) has no codified honesty/anti-fabrication/citation doctrine. SOFI agents are expected to cite `file:line` in review/audit contexts by convention, but it's not a formal, universal rule applying to every agent's every claim.

## Actionable Takeaway
Add a "Grounding" section to `00-operating-system.md` codifying: cite claims to file:line or a brain document; say "unknown, needs verification" rather than guessing; separate stated fact from inference explicitly; surface conflicting sources (e.g. a memory file vs. current code state) instead of silently trusting one. This is the single most concrete, low-effort, high-value gap surfaced across all 38 articles.
