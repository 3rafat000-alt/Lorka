#!/usr/bin/env python3
"""
Phase 1: Handoff Integrity — Triple-Contract Check Validation
ADR-006 Implementation

Enforces Contract Parity on all handoffs:
- [x] Upstream Origin: Traced to UX Prototype Screen ID
- [x] Contract Parity: API resource inputs match Flutter Cubit state signature
- [x] Data Immutable: No destructive migrations without explicit ADR in DECISIONS.md

Used by `sofi checkpoint` to reject handoffs with missing validation blocks.
Prevents semantic drift Telephone effect across multi-agent chains.
"""

import re
import sys
from typing import Tuple


class HandoffValidator:
    """
    Validates Triple-Contract Check schema in HANDOFFS.md blocks.
    """

    # Strict regex patterns for Triple-Contract Check components
    PATTERNS = {
        "upstream_origin": r'-\s*\[x\]\s*\*?\*?Upstream Origin:\*?\*?\s*Traced to UX Prototype',
        "contract_parity": r'-\s*\[x\]\s*\*?\*?Contract Parity:\*?\*?\s*API resource inputs match',
        "data_immutable": r'-\s*\[x\]\s*\*?\*?Data Immutable:\*?\*?\s*No destructive migrations',
    }

    def __init__(self, handoff_file_path: str):
        self.handoff_file_path = handoff_file_path
        self.validation_results = {}

    def read_handoff(self) -> str:
        """Read HANDOFFS.md content."""
        try:
            with open(self.handoff_file_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"HANDOFFS.md not found at {self.handoff_file_path}")

    def validate_contract_check(self, content: str) -> Tuple[bool, dict]:
        """
        Validate all three contract check components are present and checked.

        Returns:
            (is_valid, results_dict)
            results_dict: {
                "upstream_origin": bool,
                "contract_parity": bool,
                "data_immutable": bool,
                "all_present": bool,
                "missing": [list of missing components]
            }
        """
        results = {
            component: bool(re.search(pattern, content, re.IGNORECASE))
            for component, pattern in self.PATTERNS.items()
        }

        all_present = all(results.values())
        missing = [k for k, v in results.items() if not v]

        self.validation_results = {
            **results,
            "all_present": all_present,
            "missing": missing
        }

        return all_present, self.validation_results

    def format_validation_error(self) -> str:
        """Format detailed error message for rejected handoff."""
        error = "[METADATA VIOLATION] Handoff rejected!\n"
        error += "Your HANDOFFS.md block must contain fully checked Triple-Contract validation tokens.\n\n"
        error += "Required format:\n"
        error += "```markdown\n"
        error += "## Next Ticket / Handoff\n"
        error += "- [ ] **Upstream Origin:** Traced to UX Prototype Screen ID [e.g., SAKK-W-04]\n"
        error += "- [ ] **Contract Parity:** API resource inputs exactly match Flutter Cubit state signature\n"
        error += "- [ ] **Data Immutable:** No destructive migrations without explicit ADR in DECISIONS.md\n"
        error += "```\n\n"

        if self.validation_results["missing"]:
            error += f"Missing components:\n"
            for component in self.validation_results["missing"]:
                error += f"  - [ ] {component.replace('_', ' ').title()}\n"

        error += "\nRationale:\n"
        error += "- Upstream Origin: Ensures handoff traces to original design intent\n"
        error += "- Contract Parity: Prevents API/UI signature mismatches across tiers\n"
        error += "- Data Immutable: Blocks destructive DB operations without architectural review\n"

        return error

    def backfill_recent_handoffs(self, count: int = 10) -> list:
        """
        Scan recent git commits for HANDOFFS.md changes.
        Return list of commits that need backfill validation.
        """
        # This would be implemented with git history scanning
        # For now, return mock data
        return [
            {"sha": "abc123", "msg": "feat: payment flow update"},
            {"sha": "def456", "msg": "fix: KYC modal"},
        ]


def validate_sofi_checkpoint(handoff_file_path: str, verbose: bool = False) -> int:
    """
    CLI hook for `sofi checkpoint`.
    Called before git commit to validate handoff integrity.

    Returns:
        0 if valid, 1 if invalid (blocks commit)
    """
    validator = HandoffValidator(handoff_file_path)

    try:
        content = validator.read_handoff()
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return 1

    is_valid, results = validator.validate_contract_check(content)

    if is_valid:
        if verbose:
            print("[HANDOFF VALIDATED] Triple-Contract Check present ✓")
            print(f"  - Upstream Origin: {results['upstream_origin']}")
            print(f"  - Contract Parity: {results['contract_parity']}")
            print(f"  - Data Immutable: {results['data_immutable']}")
        return 0
    else:
        print(validator.format_validation_error())
        return 1


if __name__ == "__main__":
    # CLI usage: python3 handoff_validator.py <path_to_handoffs>
    handoff_path = sys.argv[1] if len(sys.argv) > 1 else "company/brain/org/HANDOFFS.md"
    exit_code = validate_sofi_checkpoint(handoff_path, verbose=True)
    sys.exit(exit_code)
