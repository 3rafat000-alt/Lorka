# Ship Your First Project for $0: Launch an MVP With Just Your AI Subscription

**Source:** https://www.aiwithmo.com/prompts/ship-your-first-project-for-zero

## Summary
Note: the fetched page content was actually in English, not Arabic as expected — proceeding with the content as retrieved. The article argues that shipping a first software project no longer requires money or dev hires: an AI coding subscription (~$20/mo) plus three free-tier services (GitHub, Vercel, Supabase) is enough to plan, build, and deploy an MVP in an afternoon. It frames the real blocker as psychological — the belief that shipping requires capital and expertise — not an actual financial constraint.

## Key Techniques / Patterns
- Nine-stage pipeline: subscribe to an agentic coder → install desktop app → create empty project folder → **plan first** (documented in markdown) → build UI first → iterate on feedback → create free GitHub/Vercel/Supabase accounts → connect services via MCP (AI handles integration) → deploy (GitHub→Vercel auto-deploy).
- Planning before building is called "the single most important stage."
- Front-end-first development to generate tangible, visible progress quickly.
- Security hygiene: set up `.gitignore` immediately so API keys/`.env` never enter version control.
- Use MCP integrations to let the AI agent wire up hosting/DB/auth rather than hand-configuring.

## Concrete Examples From the Article
- Cost breakdown: AI subscription ~$20/mo, GitHub $0, Vercel $0, Supabase $0 → total infra cost $0.
- Free-tier limits cited: Vercel free for personal/non-commercial use (~$20/mo Pro once payments/ads added); Supabase free tier = 500MB storage, 2 projects max, auto-pauses after 7 days inactivity.
- Named alternative no-code platforms: Lovable and Bolt (faster, but with platform lock-in tradeoffs).
- Claimed timeline: a full MVP "can realistically come together in an afternoon."

## Relevance to SOFI
Partially applicable as a reference pattern, not a technique SOFI lacks. SOFI already formalizes "plan before building" via its gate lifecycle (0 Inception → 4 Build) and already treats `.gitignore`/secrets hygiene as a hard rule (git-discipline protocol, hook-blocked secret commits). The article's "plan → scaffold UI first → iterate → wire services via AI → deploy" flow is a simplified, single-dev version of what SOFI's tiered agents + `new-project.sh` + `sofi domain up` already do end-to-end for a whole org rather than a solo builder. The genuinely reusable idea is the **zero-cost free-tier stack pattern** (GitHub+Vercel+Supabase) as a fast, no-budget path for spinning up a throwaway MVP/demo project — useful for SOFI's local-domain/tunnel flow when a client needs a quick, cost-free proof-of-concept before committing to the full staging/prod pipeline.

## Actionable Takeaway
Document a "$0 MVP fast-path" preset in `engine/protocols/local-domains.md` or a new scaffold flag (GitHub+Vercel+Supabase free tier) that DevOps/CEO can offer for early-stage client demos before a project earns full Gate 6/7 staging infrastructure.
