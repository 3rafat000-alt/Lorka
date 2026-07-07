#!/usr/bin/env python3
"""
Agent Pre-flight Briefing Hydration.
Every agent runs this at session start to ingest the latest binding instructions.

Authority: DOCTRINE.md Teaching VII, Protocol 02, Gemini architectural recommendation.
Purpose: Ensure agents run with current Autonomous Gemini Loop rules (not stale memory).
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SOFI_ROOT = _HERE.parents[2]  # company/ (from company/os/toolkit/core/)

# v6/v7 binding doctrine an agent must run with. (v5's AGENT_BRIEFING.md /
# DOCTRINE.md / protocols/02-autonomous-gemini-loop.md were replaced by these.)
BRIEFING_FILES = [
    "CONSTITUTION.md",
    "constitution/00-operating-system.md",
    "os/oracle/GEMINI_LOOP_ARCHITECTURE.md",
]


def hydrate_agent(prj: str = None, verbose: bool = False) -> dict:
    """
    Load latest binding instructions into agent memory.
    Returns: {status, files_loaded, total_chars, briefing_path}
    """
    results = {
        "status": "HYDRATED",
        "files_loaded": [],
        "total_chars": 0,
        "briefing_path": None,
    }

    # Compile briefing into single text block
    briefing_parts = []
    for fname in BRIEFING_FILES:
        fpath = _SOFI_ROOT / fname
        if fpath.exists():
            try:
                content = fpath.read_text(encoding="utf-8")
                briefing_parts.append(f"\n{'='*70}\n# {fname}\n{'='*70}\n\n{content}")
                results["files_loaded"].append(fname)
                results["total_chars"] += len(content)
            except Exception as e:
                if verbose:
                    print(f"⚠️  Failed to load {fname}: {e}", file=sys.stderr)
        else:
            if verbose:
                print(f"⚠️  Not found: {fname}", file=sys.stderr)

    if not briefing_parts:
        results["status"] = "FAILED_NO_FILES"
        return results

    # Save compiled briefing to a runtime override file
    briefing_text = "\n".join(briefing_parts)
    override_path = _SOFI_ROOT / ".sofi_agent_briefing_current"
    try:
        override_path.write_text(briefing_text, encoding="utf-8")
        results["briefing_path"] = str(override_path)
    except Exception as e:
        if verbose:
            print(f"❌ Failed to write briefing override: {e}", file=sys.stderr)
        results["status"] = "FAILED_WRITE"
        return results

    if verbose:
        print(f"✅ Agent hydrated: {len(results['files_loaded'])} files, {results['total_chars']} chars", file=sys.stdout)
        print(f"   Briefing: {override_path}", file=sys.stdout)

    return results


if __name__ == "__main__":
    import json
    result = hydrate_agent(verbose=True)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "HYDRATED" else 1)
