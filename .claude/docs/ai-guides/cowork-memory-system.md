# The MEMORY.md System

**Source:** https://www.aiwithmo.com/prompts/cowork-memory-system

## Summary
Long conversations waste tokens exponentially — at message 80, every reply carries 79 messages of history. The fix: move project knowledge into a permanent `MEMORY.md` file instead of letting it accumulate in chat history, and keep individual sessions short (20-30 messages).

## Key Techniques / Patterns
Four-step loop: (1) session start — read `MEMORY.md`, (2) work phase — keep it brief, (3) session end — update `MEMORY.md` with completed items/decisions/next tasks, (4) repeat with a fresh, lightweight conversation.

`MEMORY.md` template: Project Goal · Current Status · Key Decisions · Context Claude Must Know · Rules for Claude · Open Questions.

## Concrete Examples From the Article
None beyond the template/loop itself.

## Relevance to SOFI
SOFI's brain (`STATE.md` + `CONTEXT.md` + `DECISIONS.md` + `HANDOFFS.md`) already implements this pattern, more granularly than a single `MEMORY.md` file — separating live state, append-only facts, irreversible decisions, and ticket queue into distinct files rather than one. The "keep sessions short + read the file at start" discipline matches SOFI's universal contract (`sofi sync` → read brain → act → checkpoint → update brain).

## Actionable Takeaway
None — already validated, and SOFI's 4-file split is arguably more disciplined than this article's single-file template (avoids one file becoming a bottleneck merge target across concurrent sessions, which SOFI's own git-discipline protocol explicitly guards against).
