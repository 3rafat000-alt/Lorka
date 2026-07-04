# Lovable: Build a Full-Stack App Without Writing a Single Line of Code

**Source:** https://www.aiwithmo.com/prompts/lovable-dev-guide

## Summary
The article profiles Lovable, an AI-powered full-stack app builder aimed at non-technical founders: a single chat interface that produces a React frontend, Supabase database, auth, Stripe payments, and hosted deployment. It frames Lovable as solving the "technical cliff" where most no-code tools stop at the frontend, and closes with a professional 5-step workflow plus pro tips for using it efficiently.

## Key Techniques / Patterns
- Write a PRD externally (via Claude/ChatGPT) before opening the tool — MVP scope, data model, user flows, design direction, integrations.
- Paste the full PRD as the first message rather than drip-feeding requests incrementally.
- Use three purpose-built modes and pick the cheapest one for the task: Chat Mode (free, planning only, no changes applied), Agent Mode (autonomous build, consumes paid credits), Visual Edits Mode (click-to-edit UI, no prompt/credit needed).
- Reserve paid Agent credits for logic/backend work; do UI-only tweaks in Visual Edits to save cost.
- Iterate with specific, targeted follow-ups instead of vague re-requests.
- Connect GitHub for code ownership/version control before going live.
- Deploy via a built-in Share → Publish flow.
- Troubleshooting tips: paste exact error text, reference concrete DB table names, describe desired changes in words rather than re-pasting whole files.

## Concrete Examples From the Article
- 25M projects built, $200M ARR, $330M Series B (Dec 2025), $6.6B valuation; enterprise clients Klarna, Uber, Zendesk.
- Free tier: 5 messages/day. Paid: from $20/month for 500 messages.
- SOC 2 Type II + ISO 27001 certified; iOS/Android apps launched April 2026.
- 20+ integrations (Stripe, GitHub, Notion, Shopify, Slack, custom API/MCP servers).
- Explicit "Step 0 → Step 5" workflow (PRD → paste-as-first-message → targeted iteration → Visual Edits for UI → connect GitHub → publish).

## Relevance to SOFI
This is fundamentally a product profile of a consumer no-code builder, not an agent-orchestration framework — most of the funding/metrics content has no transferable technique. But two workflow patterns do generalize to SOFI: (1) the "single frozen full-context brief, never drip-fed" discipline (Step 0/Step 1) reinforces SOFI's own RCCF principle of handing an agent one complete delegation block rather than piecemeal instructions; (2) the three-mode cost-tiering (free planning vs. paid execution vs. free UI-only edits) is a consumer-facing analogue of SOFI's economic routing ladder (haiku → sonnet → fable → opus, cheapest-that-clears-the-bar).

## Actionable Takeaway
Reinforce in `/sofi-delegate` and `01-delegation-rccf.md` that every RCCF block must be a single complete, frozen brief handed to the agent up front (mirroring Lovable's PRD-first, paste-once pattern) — no incremental instruction drip after spawn.
