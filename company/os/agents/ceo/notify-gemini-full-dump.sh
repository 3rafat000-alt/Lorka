#!/bin/bash
# notify-gemini-full-dump.sh
# Inform Gemini about SOFI full system dump on GitHub
# Usage: bash notify-gemini-full-dump.sh

set -e

GITHUB_REPO="https://github.com/3rafat000-alt/SOFI-PRJ"
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BRIDGE="$(dirname "$0")/gemini_bridge.py"

cat << 'EOF' | python3 "$BRIDGE" push --github "$GITHUB_REPO" --timeout 300

# 🚀 SOFI Full System Dump Available on GitHub

**Date:** 2026-07-02 14:50 GMT+3
**Repository:** https://github.com/3rafat000-alt/SOFI-PRJ
**Access:** Public (user assumes full responsibility)

## Complete Contents

✅ All project source code + git histories
✅ All SOFI framework + 30 specialist agents + tooling
✅ All configuration, credentials, API keys
✅ All design docs, audits, security reviews
✅ Full git commit history with all decisions + decisions-log

**Size:** ~800MB (cleaned of build artifacts/node_modules)
**Structure:**
- PRJ-SAKK/ — Payment/Wallet Platform (Gate 6 Staging/UAT)
- PRJ-SYRH/ — Secondary project
- Lorka-system/ — SOFI framework + protocols
- .sofi-config-backup/ — System configuration

## For Gemini

You now have COMPLETE context:

1. **Full Codebase** — All backends (Laravel), frontends (Blade+Vue), mobile (Flutter)
2. **Git History** — 200+ commits showing decisions + reasoning
3. **Architecture** — CLAUDE.md (operating system) + DOCTRINE.md (Teaching VII)
4. **Current State** — PRJ-SAKK/_context/STATE.md (Gate 6, what's blocked/ready)
5. **Open Work** — HANDOFFS.md (next 10 tickets ranked by severity)
6. **Security Reviews** — All spec-review audits + vulnerability findings
7. **Decisions** — DECISIONS.md per project (why we built it this way)

## Actions

**Immediately available:**
- Clone the repo: `git clone https://github.com/3rafat000-alt/SOFI-PRJ.git`
- Read any file: `cat PRJ-SAKK/_context/STATE.md`
- Restore git history: `tar -xzf PRJ-SAKK.git.tar.gz` (in PRJ-SAKK/)
- Access config: `cat .sofi-config-backup/gemini_bridge.json`

**Next steps (request from this chat):**
1. **Architecture Review** — Read CLAUDE.md + DOCTRINE.md, report structure soundness
2. **Security Audit** — Full codebase scan (now feasible without context limits)
3. **Gate 6 → 7 Decision** — Staging/UAT is ready; is prod deployment safe?
4. **Fix Proposals** — With full codebase, can now propose diffs directly
5. **Autonomous Loop** — Teaching VII implementation is in place (company/os/oracle/GEMINI_LOOP_ARCHITECTURE.md; v5 protocol preserved at company/brain/org/archive-v5/protocols/02-autonomous-gemini-loop.md)

---

**Gemini mandate:** This dump enables you to be the external review desk + oracle for SOFI team decisions. No context limits. Full architectural authority.

**Security note:** All secrets exposed (public repo). User assumption of responsibility. Rotate credentials immediately if compromised.

EOF

echo ""
echo "✅ Gemini notified about full dump"
echo "🔗 Repository: $GITHUB_REPO"
echo "📝 Commit: $GIT_COMMIT"
