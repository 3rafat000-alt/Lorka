# ⚡ Performance Budget (Core Web Vitals)

Quantified thresholds harvested from the old SOFI teams. Owner: **Ahmed** (Performance & Load Analyst, Gate 5). Gate 5 **rejects** anything that breaches these; Gate 8 (Naomi) alerts on field regressions.

> "Speed is not a feature — it's an expectation."

| Metric | Good ✓ | Needs work ⚠ | Bad ✗ |
|---|---|---|---|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | 2.5–4.0s | > 4.0s |
| **INP** (Interaction to Next Paint) | ≤ 200ms | 200–500ms | > 500ms |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | 0.1–0.25 | > 0.25 |
| **TTFB** (Time to First Byte) | ≤ 200ms | 200–500ms | > 500ms |
| **TTI** (Time to Interactive) | **< 2s** (hard gate) | — | ≥ 2s → rejected |

**Fix ladder:**
- **LCP** — WebP/AVIF, lazy-load below the fold, CDN static, preload the hero.
- **INP** — code-split, defer non-critical JS, Web Workers for heavy compute, trim event handlers.
- **CLS** — set width/height on media, reserve space for async content, avoid layout-shifting injects.
- **TTFB** — cache (Redis/CDN/browser), kill N+1 (Günther: EXPLAIN hot queries), index hot paths.

Measure: Lighthouse/CWV in CI (Gate 5) + CrUX field data (Gate 8). Budget breach = blocker, not a warning.
