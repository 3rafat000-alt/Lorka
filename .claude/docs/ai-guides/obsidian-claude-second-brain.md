# Build Your AI Second Brain: Obsidian + Claude + Steph Ango's Official Skills

**Source:** https://www.aiwithmo.com/prompts/obsidian-claude-second-brain

## Summary
Note: the fetched page rendered in English (`lang="en"`), not Arabic, despite the site metadata listing both `ar`/`en`. The article argues that pairing Claude Code with an Obsidian vault (plain local Markdown files) solves Claude's session-reset amnesia and turns a note pile into a self-linking knowledge base. It leans on two January 2026 catalysts: Obsidian CEO Steph Ango ("kepano") releasing an official `obsidian-skills` repo, and Andrej Karpathy publicly endorsing plain-Markdown-plus-LLM over RAG/vector-DB pipelines. The core claim: Claude reading a whole vault can surface relationships a human would miss and wire the links itself.

## Key Techniques / Patterns
- **`CLAUDE.md` at the vault root** — read automatically every session; encodes folder structure, tagging schema, note templates, and rules ("your contract with the AI").
- **YAML frontmatter on every note** (minimum: `date`, `tags`, `status`, `type`) — turns a folder of text files into a queryable database (e.g., "all notes with status active and tag project-alpha").
- **PARA folder method** (Projects / Areas / Resources / Archive) for inbox triage.
- **Outcome-framed prompts, not instruction-framed ones** — ask for the result ("find related notes and link them both ways, explain why") rather than a procedure.
- **Bidirectional wikilinking as a standing task** — run periodically so the graph compounds (50th note is far more connected than the 1st because Claude cross-references the whole vault).
- **`obsidian-skills`** (github.com/kepano/obsidian-skills) — five official skills teaching correct syntax for wikilinks, frontmatter, Bases (JSON databases), Canvas (spatial maps), and the Obsidian CLI, preventing broken links/invalid files.
- **Strip-before-save**: use `defuddle` to convert web pages to clean Markdown before saving into the vault, cutting token cost.

## Concrete Examples From the Article
- Stats: `obsidian-skills` hit 13,900+ GitHub stars within weeks; Karpathy's markdown-over-RAG post hit ~14,000 stars in a week; `defuddle` cuts token cost by ~60%.
- Sample prompt: "Scan all notes in `3. Resources/` added this week. For each new note, find 3-5 existing notes it relates to and add `[[wikilinks]]` to both files."
- Sample prompt: "Go through every file in `0. Inbox/`. For each one: determine the correct PARA category, move it to the right folder, add proper frontmatter, link it to 2-3 related existing notes."
- Sample prompt: "What have I decided about [topic]? Check my decision notes and quote the relevant parts with file references."
- Other named workflows: building topic wiki pages that synthesize a subject, and weekly synthesis runs that surface decisions, open questions, and new cross-project connections.

## Relevance to SOFI
Directly applicable, and it validates SOFI's own architecture rather than introducing something new. SOFI's `_context/{STATE,CONTEXT,DECISIONS,HANDOFFS}.md` brain is exactly this pattern: plain Markdown, git-backed, read at session start (the article's `CLAUDE.md`-at-root habit mirrors SOFI's "no blind start" rule). Two transferable refinements: (1) the article's frontmatter-as-queryable-metadata trick — SOFI's brain files could gain light YAML frontmatter (`status`, `gate`, `type`) to make cross-project queries (e.g., "all tickets with status blocked") mechanical instead of grep-only; (2) the outcome-framed-prompt discipline and periodic "relink/synthesize" pass maps cleanly onto `/sofi-handoff` and `/sofi-report` — a scheduled "synthesis" sweep across `HANDOFFS.md`/`DECISIONS.md` (surfacing decisions, open questions, stale threads) would be a cheap `haiku`-tier addition to the gate-exit routine.

## Actionable Takeaway
Add optional YAML frontmatter (`status`, `gate`, `type`, `date`) to `STATE.md`/`HANDOFFS.md` ticket entries so `sofi` tooling can query the brain structurally instead of only via grep — low effort, directly reuses a technique the article demonstrates working at scale.
