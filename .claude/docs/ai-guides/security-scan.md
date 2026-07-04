# Code Guardian: Automated Multi-Phase Security Scanner

**Source:** https://www.aiwithmo.com/prompts/security-scan

## Summary
The article presents "Code Guardian," a Claude Code skill that turns Claude into an automated cybersecurity engineer for full codebases. It first inspects project structure to decide how many scan phases are needed (1-2 for small projects, 3-4 medium, 5-6 large), then runs each phase against a specific architectural layer (auth, API routes, database, frontend, config, third-party integrations), producing a severity-ranked Markdown report per phase plus a final aggregated executive summary.

## Key Techniques / Patterns
- Dynamic phase allocation: scan depth scales with codebase size/complexity rather than a fixed checklist.
- Domain-specific scan phases, each scoped to one architectural layer (auth, APIs, DB, frontend, env config, integrations).
- Per-finding severity classification (Critical/High/Medium/Low).
- Each vulnerability ships with an "Execution Plan" — a fix checklist formatted for handoff to an AI coding agent (e.g. Lovable, Cline) to execute directly.
- Aggregated final report cross-references detailed per-phase files, sorted by severity.
- Stack-adaptive: works across different full-stack architectures rather than one fixed tech stack.

## Concrete Examples From the Article
- Phase file naming convention: `scan-phase-1-auth-layer.md`.
- Final output file: `scan-summary.md` as the master dashboard.
- Project-size-to-phase-count mapping: small (1-2), medium (3-4), large (5-6).
- Target vulnerability classes named: injection attacks, broken access control, exposed secrets, insecure dependencies, XSS, CSRF, improper error handling.

## Relevance to SOFI
Directly applicable — this maps almost one-to-one onto `/sofi-secure` and `/sofi-audit`. SOFI already does grep-first, layered scanning (ui/blade/css/js/db/api/integration/agents), but the article's **dynamic phase-count scaling by project size** and **per-finding AI-executable Execution Plans** are concrete refinements worth adopting: instead of a flat severity list, each SEV finding could carry a ready-to-delegate fix checklist scoped for the exact specialist agent that will pick it up in `/sofi-fix`, tightening the audit→fix handoff.

## Actionable Takeaway
Extend `/sofi-secure` findings to include a per-vulnerability "Execution Plan" block (concrete fix steps pre-formatted for the specialist agent `/sofi-fix` will delegate to), and scale scan-phase count to project size the way `/sofi-audit` already scales by layer — closing the gap between "found" and "assigned-fixable" in one step.
