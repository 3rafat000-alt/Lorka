#!/usr/bin/env bash
# SOFI tooling: unit selftests + a live end-to-end pipeline demo.
# Runs everything under a throw-away SOFI_HOME so the real .sofi is untouched.
set -u
cd "$(dirname "$0")"

echo "================ 1) unit selftests ================"
python3 sofi selftest || { echo "UNIT SELFTESTS FAILED"; exit 1; }

echo
echo "================ 2) live pipeline demo ============"
SOFI_HOME="$(mktemp -d)"; export SOFI_HOME
trap 'rm -rf "$SOFI_HOME"' EXIT
echo "(isolated SOFI_HOME=$SOFI_HOME)"

echo "--- a) validate a delegation payload (Maestro guard) ---"
python3 validate.py delegation --payload \
  '{"sender":"CEO_Agent","recipient":"bck-api-engineer","action":"CREATE_MIGRATION","parameters":{"table":"users"},"context_priority":"HIGH"}' \
  --json || { echo "validate failed"; exit 1; }

echo "--- b) gateway: structured intent -> validated -> enqueued ---"
python3 gateway.py ingest --payload \
  '{"instruction_type":"FEATURE_EXPANSION","priority":"HIGH","target_stacks":["Laravel_v12","Vue3"],"summary":"add phone to profile","actions":[{"sub_system":"BACKEND","task":"phone_number migration + validation"},{"sub_system":"WEB_UI","task":"profile phone field + state + API"}]}' \
  --json || { echo "gateway ingest failed"; exit 1; }

echo "--- c) registry: backend publishes new schema (SSoT) ---"
python3 registry.py set-table users --fields \
  '[{"name":"id","type":"bigint"},{"name":"phone_number","type":"string","nullable":true}]' --json >/dev/null
python3 registry.py set-contract 'POST /api/v1/profile' --method POST --path /api/v1/profile \
  --request '{"phone_number":"string"}' --response '{"ok":"bool"}' --json >/dev/null
python3 registry.py dump --json

echo "--- d) taskq: drive task #1 through the state machine ---"
python3 taskq.py assign 1 --to bck-api-engineer --json >/dev/null
python3 taskq.py start 1 --json >/dev/null
python3 taskq.py done 1 --result '{"migration":"2026_07_09_add_phone.php"}' --json >/dev/null
python3 taskq.py stats --json

echo "--- e) gitflow guard: dangerous ops are refused ---"
python3 gitflow.py guard-check "git push --force" --json
python3 gitflow.py guard-check "git reset --hard HEAD~1" --json

echo
echo "================ DEMO OK ================"
