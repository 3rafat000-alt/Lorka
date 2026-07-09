#!/usr/bin/env bash
set -euo pipefail

# Pre-tool hook — security + git guard
# Blocks: destructive git, .env manipulation, secrets in code
# Fails open on error (exit 0) — never block benign operations

OPENCODE_COMMAND="${OPENCODE_COMMAND:-}"

# === BLOCK: Destructive git ===
if echo "$OPENCODE_COMMAND" | grep -qE '(git reset --hard|git push --force|git push -f)'; then
  echo "❌ BLOCKED: Destructive git operation detected."
  echo "   Route to Gemini first via autonomous loop."
  exit 1
fi

# === BLOCK: .env manipulation ===
if echo "$OPENCODE_COMMAND" | grep -qE '(rm|mv|cp|chmod).*\.env"|\.env.*(delete|remove)'; then
  echo "❌ BLOCKED: .env file manipulation not allowed."
  echo "   Use vault or settings system instead."
  exit 1
fi

# === WARN: Secrets in staged code ===
if echo "$OPENCODE_COMMAND" | grep -qE '(git commit|git add)'; then
  if git diff --cached --name-only 2>/dev/null | xargs grep -lE '(api.?key|secret|password|token|sk_live|pk_live)' 2>/dev/null; then
    echo "⚠️  WARNING: Potential secrets detected in staged files."
    echo "   Review before committing. If intentional, add to .gitleaksignore."
    # Warn-only (fail open) — allows override
  fi
fi

# === BLOCK: DROP TABLE / destructive DB ===
if echo "$OPENCODE_COMMAND" | grep -qEi '(DROP TABLE|DROP DATABASE|TRUNCATE)'; then
  echo "❌ BLOCKED: Destructive database operation."
  echo "   Use reversible migration or ADR + rollback plan."
  exit 1
fi

# === BLOCK: npm publish / composer publish ===
if echo "$OPENCODE_COMMAND" | grep -qE '(npm publish|composer publish)'; then
  echo "❌ BLOCKED: Package publish requires release workflow."
  exit 1
fi

exit 0
