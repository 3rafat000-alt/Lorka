#!/bin/bash
# Agent Output Guard Wrapper
# Usage: agent_wrapper.sh <PRJ> <AGENT_COMMAND...>
#
# Before agent output reaches user, this wrapper:
# 1. Captures agent stdout
# 2. Runs through output_guard.py
# 3. Halts on violation (direct user ask detected)
# 4. Otherwise passes output through

set -euo pipefail

PRJ="${1:?PRJ-ID required (e.g., PRJ-SAKK)}"
shift

_HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Run agent, capture output
agent_output=$("$@" 2>&1) || {
    agent_exit=$?
    # Even on agent error, check output for violations
    echo "$agent_output" | python3 "$_HERE/agent_output_guard.py" "$PRJ" 2>&1 || exit "$?"
    exit "$agent_exit"
}

# Check output for violations (guard mode)
echo "$agent_output" | python3 "$_HERE/agent_output_guard.py" "$PRJ" 2>&1

exit 0
