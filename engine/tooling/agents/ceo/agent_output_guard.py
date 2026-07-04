#!/usr/bin/env python3
"""
Agent Output Guard — Runtime Interceptor.
Blocks any agent from asking the user directly.
Halts + redirects to Gemini if violation detected.

Authority: DOCTRINE.md Teaching VII, Protocol 02 §5 Enforcement.
"""
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent

# Patterns that indicate agent is asking the user (banned)
VIOLATION_PATTERNS = [
    # Direct questions
    r'\bما\s+(?:الخطوة|الحل|التالي|رأيك|تفضل)\b',
    r'\bأي(?:\ة)?\s+(?:منهما|الخيارات|المسارات|الطريقة)\b',
    r'\bهل\s+(?:يجب|يمكن|تفضل|توافق)\b',
    r'\bكيف\s+(?:تفضل|توافق|نقرر)\b',
    r'\bماذا\s+(?:تنصح|توصي|تقترح)\b',

    # English equivalents
    r'\bwhich\s+(?:option|path|approach)\b',
    r'\bwhat\s+(?:should|would)\s+you\b',
    r'\bdo\s+you\s+(?:think|prefer|recommend)\b',
    r'\byour\s+(?:input|decision|guidance)\b',
    r'\bwhat\s+(?:do\s+you\s+)?think\b',

    # Generic human-ask markers
    r'\bيرجى\s+(?:تحديد|اختيار|الإجابة)\b',
    r'\bأرجو\s+(?:التوجيه|الإجابة|التصحيح)\b',
    r'\bمساعدتك\b',
    r'\bتدخلك\b',
]

def check_output(text: str) -> tuple[bool, str | None]:
    """
    Check if output violates autonomous loop rule.
    Returns: (is_clean, violation_text)
    """
    for pattern in VIOLATION_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return False, match.group(0)
    return True, None


def halt_and_redirect(agent_output: str, violation: str, prj: str) -> None:
    """
    Halt execution. Print guard message. Redirect to Gemini review.
    """
    error_msg = f"""
╔════════════════════════════════════════════════════════════════╗
║ ❌ AUTONOMOUS LOOP VIOLATION — HALTED                          ║
╚════════════════════════════════════════════════════════════════╝

Violation: Agent attempted direct user ask.
Pattern found: "{violation}"

Rule: All decisions → Gemini desk. Never ask the user directly.
Authority: DOCTRINE.md Teaching VII, Protocol 02 §5

Command to route decision to Gemini:
  sofi gemini review --prj {prj} --json \\
    --text "Agent output: {agent_output[:200]}..." \\
    --ask "What should the agent do? Prioritize."

This process has been halted. Uncommitted changes remain (safe).
Next: Route the decision to Gemini, execute the reply.
"""
    print(error_msg, file=sys.stderr)
    sys.exit(1)


def guard_output(text: str, prj: str = "PRJ-UNKNOWN") -> str:
    """
    Main entry point. Check output and halt if violation.
    Returns cleaned text if safe.
    """
    is_clean, violation = check_output(text)
    if not is_clean:
        halt_and_redirect(text, violation, prj)
    return text


# ── CLI entry point ────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    prj = sys.argv[1] if len(sys.argv) > 1 else "PRJ-UNKNOWN"
    text = sys.stdin.read()
    try:
        result = guard_output(text, prj)
        print(result, end='')
        sys.exit(0)
    except SystemExit as e:
        # halt_and_redirect calls sys.exit(1), which we let through
        sys.exit(e.code)
