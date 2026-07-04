# Reverse Prompt Engineering: Let the AI Write the Perfect Prompt For You in One Step

**Source:** https://www.aiwithmo.com/prompts/reverse-prompt-engineering

## Summary
This guide flips traditional prompt writing: instead of crafting the perfect prompt upfront (always a guess, even for experts), have a normal iterative conversation with the model — correcting and refining until output quality is right — then run a structured "extraction prompt" asking the model to compress everything learned into one reusable master prompt. This turns a multi-turn conversation into a single reusable artifact and builds a prompt library grounded in real work rather than theory.

## Key Techniques / Patterns
- **Iterative discovery first** — let requirements surface naturally through conversation and corrections rather than pre-specifying them.
- **End-stage extraction** — once output quality is satisfactory, issue a dedicated extraction prompt that asks the model to synthesize the full conversation into one master prompt.
- **Extraction prompt variants** — the article gives three forms: a full version, a shortened version, and a template version (with bracketed variables for the parts that change per use).
- **Library building** — save extracted prompts into Markdown files organized by task category (e.g., content writing, research analysis, code review).
- **Extraction threshold** — worth doing once a conversation exceeds roughly 5+ correction/refinement messages.
- Model-agnostic — works across Claude, ChatGPT, and Gemini.

## Concrete Examples From the Article
- A "fifteen-message conversation" reduced to "one message and one reply" via the extracted master prompt.
- Three concrete extraction-prompt templates provided (full/shortened/template forms) — the mechanism for turning conversation into artifact.
- Suggested library structure: Markdown files split by task category.

## Relevance to SOFI
Directly applicable. SOFI already has a "protocols as frozen artifacts" pattern (RCCF blocks, `engine/protocols/`), but this article's specific technique — mining a real, corrected conversation for a reusable prompt rather than authoring specs cold — maps well onto agent Operating Prompts and delegation templates. When a CEO/agent iterates live with a specialist to get a task right, that corrected exchange is higher-signal than a hand-written RCCF block, and could itself be distilled into the reusable template for the next similar delegation.

## Actionable Takeaway
Add an "extract-to-template" step to `/sofi-delegate`: after any RCCF spawn that required 2+ correction rounds to converge, run an extraction pass that folds the corrections into an updated reusable RCCF template for that agent+task-type, stored under `engine/protocols/` or the agent's spec — so the org's delegation library improves from lived corrections instead of staying static.
