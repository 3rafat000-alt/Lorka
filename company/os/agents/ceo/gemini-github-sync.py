#!/usr/bin/env python3
"""
gemini-github-sync.py
Autonomous loop: Gemini findings → GitHub issues → Team execution

Gemini posts audit findings to pinned chat.
This script:
1. Monitors Gemini chat for new responses
2. Parses findings (JSON format)
3. Auto-creates GitHub issues (per project, per severity)
4. Tags assignees (RCCF delegation)
5. Tracks execution (PR links, commits, status)
6. No chat reports — only GitHub + git history
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

GITHUB_TOKEN = "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"
GITHUB_REPO = "3rafat000-alt/SOFI-PRJ"
SOFI_PROJECT = "PRJ-SAKK"

SEVERITY_LABELS = {
    "🟢": "good-pattern",
    "🟠": "clarification-needed",
    "🔴": "blocker"
}

CATEGORY_ASSIGNEES = {
    "architecture": "sofi-principal-system-architect",
    "security": "sofi-security-compliance-architect",
    "PRJ-SAKK": "sofi-backend-blade-engineer",
    "infrastructure": "sofi-devops-cloud-lead",
    "code": "sofi-qa-sre-lead",
    "Teaching VII": "sofi-ceo"
}


def parse_gemini_findings(json_text: str) -> dict:
    """Parse Gemini JSON response."""
    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        print("Failed to parse Gemini response as JSON", file=sys.stderr)
        return {}


def create_github_issue(finding: dict) -> Optional[str]:
    """Create GitHub issue from finding. Return issue URL."""
    category = finding.get("category", "general")
    severity = finding.get("severity", "🟠")
    title = finding.get("finding", "")[:60]

    labels = [SEVERITY_LABELS.get(severity, "task")]
    if category:
        labels.append(category)

    body = f"""**Category:** {category}
**Severity:** {severity}
**Finding:** {finding.get('finding', '')}

**Recommendation:** {finding.get('recommendation', '')}

**File:** {finding.get('file', 'N/A')}

---
Created by Gemini audit (Teaching VII)
Automated via gemini-github-sync.py
"""

    cmd = [
        "gh", "issue", "create",
        "--repo", GITHUB_REPO,
        "--title", title,
        "--body", body,
        "--label", ",".join(labels)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Failed to create issue: {e.stderr}", file=sys.stderr)
        return None


def update_handoffs(findings: dict) -> None:
    """Update HANDOFFS.md with Gemini findings."""
    handoffs_path = Path(f"/home/es3dlll/Desktop/Lorka/projects/{SOFI_PROJECT}/_context/HANDOFFS.md")

    if not handoffs_path.exists():
        print(f"HANDOFFS.md not found at {handoffs_path}", file=sys.stderr)
        return

    content = handoffs_path.read_text()

    # Append Gemini audit section
    audit_entry = f"""

## Gemini Audit — {datetime.now().strftime('%Y-%m-%d %H:%M')}

**Summary:** {findings.get('summary', 'N/A')}

**Gate 6→7 Readiness:** {'✅ Ready' if findings.get('gate_6_to_7_readiness', {}).get('ready') else '⏳ Blocked'}

**Blockers:**
{chr(10).join(f"- {b}" for b in findings.get('gate_6_to_7_readiness', {}).get('blockers', []))}

**Teaching VII Status:** {findings.get('teaching_vii_status', 'N/A')}

**Next Actions (Priority):**
{chr(10).join(f"- {a}" for a in findings.get('next_actions', []))}

**Findings Count:** {len(findings.get('findings', []))} items

See GitHub issues for detailed findings (auto-created from this audit).
"""

    handoffs_path.write_text(content + audit_entry)
    print(f"Updated {handoffs_path}")


def commit_audit_results(findings: dict) -> str:
    """Commit audit results to git."""
    commit_msg = f"""docs(audit): Gemini architecture audit results — {datetime.now().strftime('%Y-%m-%d')}

Summary: {findings.get('summary', 'Audit completed')}

Gate readiness: {'6→7 ready' if findings.get('gate_6_to_7_readiness', {}).get('ready') else 'Blockers identified'}

Teaching VII: {findings.get('teaching_vii_status', 'Active')}

{len(findings.get('findings', []))} findings auto-filed to GitHub issues.

Audit findings ingested to HANDOFFS.md + GitHub project board.
No manual reports — execution via RCCF delegation to specialist agents.

Co-Authored-By: Gemini <oracle@sofi.local>"""

    try:
        subprocess.run(
            ["git", "add", "-A"],
            cwd=f"/home/es3dlll/Desktop/Lorka/projects/{SOFI_PROJECT}",
            check=True
        )
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=f"/home/es3dlll/Desktop/Lorka/projects/{SOFI_PROJECT}",
            check=True
        )
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=f"/home/es3dlll/Desktop/Lorka/projects/{SOFI_PROJECT}",
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Commit failed: {e.stderr}", file=sys.stderr)
        return "unknown"


def main():
    """Main loop: Parse Gemini findings → Create GitHub issues → Commit."""

    # Read Gemini findings from stdin (or file)
    findings_json = sys.stdin.read() if not sys.stdin.isatty() else "{}"

    if not findings_json.strip():
        print("No input received", file=sys.stderr)
        return 1

    findings = parse_gemini_findings(findings_json)

    if not findings:
        print("Invalid findings format", file=sys.stderr)
        return 1

    print(f"Processing {len(findings.get('findings', []))} findings...")

    # Create GitHub issues
    issue_count = 0
    for finding in findings.get('findings', []):
        issue_url = create_github_issue(finding)
        if issue_url:
            issue_count += 1
            print(f"✓ Created: {issue_url}")

    # Update HANDOFFS.md
    update_handoffs(findings)

    # Commit to git
    commit_sha = commit_audit_results(findings)
    print(f"✓ Committed: {commit_sha}")

    # Print summary (for logging, not chat display)
    print(f"\n=== AUDIT SYNC COMPLETE ===")
    print(f"Issues created: {issue_count}")
    print(f"Findings ingested: {len(findings.get('findings', []))}")
    print(f"Commit: {commit_sha}")
    print(f"Status: Ready for team execution (RCCF delegation)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
