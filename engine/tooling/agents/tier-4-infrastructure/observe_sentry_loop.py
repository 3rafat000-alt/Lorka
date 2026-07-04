#!/usr/bin/env python3
"""
Phase 5: Observe Loop — Gate 8 Feedback Hook
ADR-006 Implementation

Polls Sentry for high-frequency exceptions (24h window, error rate >threshold).
Classifies root cause (data constraint / API contract / user input / perf).
Injects runtime-observed constraints into _context/DECISIONS.md for future code generation.

Closes the feedback loop: Production Anomaly → Project Brain Update
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import re


class SentryObserver:
    """
    Gate 8 Observer: Sentry → DECISIONS.md feedback loop.
    """

    def __init__(self, prj_id: str):
        self.prj_id = prj_id
        self.project_root = os.path.expanduser(f"~/Desktop/Lorka/projects/PRJ-{prj_id}")
        self.decisions_path = os.path.join(self.project_root, "_context", "DECISIONS.md")

    def poll_sentry(self, hours: int = 24, error_rate_threshold: float = 0.01) -> List[Dict]:
        """
        Poll Sentry for high-frequency exceptions in recent window.

        In production, use Sentry SDK:
        ```python
        from sentry_sdk.integrations.httpx import HttpxIntegration
        import sentry_sdk
        client = sentry_sdk.Hub.current.client
        issues = client.get_issues(projects=[self.prj_id], statsPeriod=f"{hours}h")
        ```

        For now, return mock data.

        Returns:
            [
                {
                    "id": "issue_123",
                    "title": "ExchangeRateRounding: precision loss",
                    "error_rate": 0.02,
                    "count": 150,
                    "first_seen": "2026-07-02T10:30:00Z",
                    "stack_trace": "..."
                },
                ...
            ]
        """
        return [
            {
                "id": "issue_001",
                "title": "ExchangeRateRounding: precision loss on large conversions",
                "error_rate": 0.015,
                "count": 45,
                "category": "DATA_CONSTRAINT",
                "stack_trace": "exchange.py:152 in convert_amount()"
            },
            {
                "id": "issue_002",
                "title": "KYC validation accepts invalid photo dimensions",
                "error_rate": 0.008,
                "count": 24,
                "category": "USER_INPUT",
                "stack_trace": "kyc_service.py:89 in validate_photo()"
            }
        ]

    def classify_root_cause(self, exception: Dict) -> Dict:
        """
        Classify exception root cause.

        Returns:
            {
                "category": "DATA_CONSTRAINT" | "API_CONTRACT" | "USER_INPUT" | "PERF",
                "tier": "DESIGN" | "ARCHITECTURE" | "BUILD",
                "action": "design review" | "schema migration" | "input validation"
            }
        """
        title = exception.get("title", "").lower()

        # Pattern-match categories
        if any(x in title for x in ["precision", "rounding", "magnitude", "currency", "rate", "conversion"]):
            return {
                "category": "DATA_CONSTRAINT",
                "tier": "ARCHITECTURE",
                "action": "Review numeric precision requirements + update schema/validation"
            }
        elif any(x in title for x in ["contract", "signature", "api", "response", "payload", "shape"]):
            return {
                "category": "API_CONTRACT",
                "tier": "ARCHITECTURE",
                "action": "Verify API/UI contract parity + update Form Request/Cubit state"
            }
        elif any(x in title for x in ["validation", "input", "format", "length", "dimension", "invalid"]):
            return {
                "category": "USER_INPUT",
                "tier": "BUILD",
                "action": "Strengthen input validation + expand test coverage"
            }
        elif any(x in title for x in ["timeout", "slow", "latency", "memory", "cpu", "load"]):
            return {
                "category": "PERF",
                "tier": "OPTIMIZATION",
                "action": "Profile + optimize hot path"
            }
        else:
            return {
                "category": "UNKNOWN",
                "tier": "UNKNOWN",
                "action": "Manual review needed"
            }

    def append_runtime_constraint_to_brain(self, exception: Dict, classification: Dict):
        """
        Append runtime observation to project DECISIONS.md.
        Future code generations will consider this constraint.
        """
        timestamp = datetime.now().isoformat()
        issue_id = exception.get("id", "unknown")
        title = exception.get("title", "")
        count = exception.get("count", 0)
        error_rate = exception.get("error_rate", 0)

        entry = f"""

## [RUNTIME_OBSERVATION] {issue_id} - {timestamp}
**Source:** Automated Sentry Gate-8 Sync
**Constraint:** {title}
**Occurrence:** {count} in last 24h ({error_rate*100:.1f}% error rate)
**Category:** {classification['category']}
**Tier:** {classification['tier']}
**Recommended Action:** {classification['action']}

**Context:** This constraint was observed in production and must be explicitly addressed in future code generations to prevent recurrence.

**Decision:** [PENDING MANUAL REVIEW]
"""

        # Append to DECISIONS.md
        if os.path.exists(self.decisions_path):
            with open(self.decisions_path, "a") as f:
                f.write(entry)
            print(f"[OBSERVE LOOP] Appended {issue_id} to {self.prj_id} brain")
        else:
            print(f"[WARNING] DECISIONS.md not found at {self.decisions_path}")

    def run_observe_cycle(self) -> int:
        """
        Execute one complete observe cycle:
        1. Poll Sentry (24h, high-frequency)
        2. Classify each exception
        3. Append to DECISIONS.md
        4. Report summary

        Returns: count of observations ingested
        """
        print(f"[OBSERVE] Starting cycle for {self.prj_id}...")

        exceptions = self.poll_sentry(hours=24, error_rate_threshold=0.01)

        if not exceptions:
            print(f"[OBSERVE] No high-frequency exceptions in last 24h")
            return 0

        print(f"[OBSERVE] Found {len(exceptions)} high-frequency exceptions")

        for exception in exceptions:
            classification = self.classify_root_cause(exception)
            self.append_runtime_constraint_to_brain(exception, classification)

        print(f"[OBSERVE] Cycle complete. {len(exceptions)} observation(s) ingested.")
        return len(exceptions)


def main():
    """Test harness."""
    prj_id = "PRJ-SAKK"
    observer = SentryObserver(prj_id)

    count = observer.run_observe_cycle()
    sys.exit(0 if count >= 0 else 1)


if __name__ == "__main__":
    import sys
    main()
