# Create a Brand Identity Skill (Claude)

**Source:** https://www.aiwithmo.com/prompts/brand-skill-duide

## Summary
The article is a prompt-engineering guide (in English, despite the site being generally Arabic-language) for building a reusable "brand identity" Skill file for Claude. It walks through a 5-step interview process that collects a brand's identity attributes and packages them into an installable `.skill` (SKILL.md + assets, zipped) so that every visual artifact Claude generates afterward (docs, decks, reports, social posts) automatically follows consistent branding.

## Key Techniques / Patterns
- Structure brand capture as a **5-step sequential interview**: (1) foundational attributes — name, personality descriptors, language direction, sub-brand structure; (2) color palette extraction, classified into primary/secondary/background; (3) typography mapping with fallback fonts for accessibility; (4) layout/mode preferences and design aesthetic; (5) compile everything into a structured `SKILL.md`.
- Emit the final skill as **YAML frontmatter + color tables with RGB values + code snippets**, then package as a ZIP for installation.
- Treat brand consistency as an **installable, reusable capability** rather than a one-off style instruction repeated per prompt.

## Concrete Examples From the Article
The article's core deliverable is a single reusable master prompt that instructs an assistant to walk a user through the five steps above, asking specific questions and producing specific deliverables (attribute list, color table, font map, layout spec, packaged SKILL.md) at each stage. No case study, company example, or numeric data is given beyond this template itself.

## Relevance to SOFI
Directly applicable, though narrow. SOFI already treats "Design is Truth" as doctrine and has a `sofi-design-taste` skill with dials + brand presets applied at Gate 2/4. This article's 5-step interview pattern is a concrete, reusable structure for *capturing* a client/project's brand identity once and packaging it as a durable artifact — analogous to how SOFI's RCCF blocks package delegation context. It's a technique for turning tacit brand knowledge into a structured, reusable spec, which fits SOFI's "reusable code → shared-packages, never duplicated" rule applied to design context instead of code.

## Actionable Takeaway
Adopt the 5-step brand-capture interview as the intake procedure for a project's brand preset: have the UI/UX lead (Dan) or `sofi-design-taste` run it once per project at Gate 2, and store the resulting structured brand spec (attributes, color table, font map, layout rules) in the project's `_context/` brain so every downstream designer/frontend agent references the same source instead of re-deriving brand rules per screen.
