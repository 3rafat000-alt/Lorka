"""
SOFI Reflection Engine — Self-evaluation, pattern detection, learning.

After every cycle: score 0–1, extract insight, detect failure patterns.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("sofi.reflection")


@dataclass
class CycleResult:
    """Result of one OODA cycle for reflection."""
    task: str = ""
    classification: str = ""
    plan: List[str] = field(default_factory=list)
    tool_calls: List[Dict] = field(default_factory=list)
    result: Any = None
    duration_ms: float = 0.0
    success: bool = False


class ReflectionEngine:
    """Self-evaluation + pattern detection + memory updates.

    After each task:
    1. Score 0.0–1.0
    2. Extract key insight
    3. Store in vector memory
    4. Detect failure patterns -> alert
    """

    def __init__(self, memory: Any, llm: Any):
        self.memory = memory
        self.llm = llm
        self.history: List[CycleResult] = []
        self.failure_alerts_sent: set = set()

    def evaluate(self, cycle: CycleResult) -> Dict:
        """Evaluate cycle result. Returns reflection dict."""
        reflection = {
            "score": 0.5,
            "goal_achieved": cycle.success,
            "key_insight": "",
            "improvements": [],
            "failure_pattern": False,
            "alert_human": False,
        }

        # Quick heuristic score
        if cycle.success:
            reflection["score"] = 0.8 + (0.2 if cycle.duration_ms < 30000 else 0.0)
        else:
            reflection["score"] = 0.2
            reflection["improvements"].append("Check tool result — task failed")

        # Estimate goal achievement
        if cycle.result:
            result_str = str(cycle.result).lower()
            if "error" in result_str or "fail" in result_str or "exception" in result_str:
                reflection["score"] = min(reflection["score"], 0.3)
                reflection["goal_achieved"] = False
            elif "success" in result_str or "ok" in result_str or "done" in result_str:
                reflection["score"] = max(reflection["score"], 0.7)
                reflection["goal_achieved"] = True

        # Duration-aware adjustment
        if cycle.duration_ms > 120_000 and reflection["score"] > 0.5:
            reflection["score"] -= 0.1
            reflection["improvements"].append("Task took >2min — optimize")

        # Use LLM for deep reflection (if available)
        if self.llm and hasattr(self.llm, "reflect"):
            try:
                llm_reflection = self._llm_reflect(cycle)
                if llm_reflection:
                    reflection.update(llm_reflection)
            except Exception as e:
                logger.debug(f"LLM reflection skipped: {e}")

        # Failure pattern detection
        self.history.append(cycle)
        pattern = self._detect_failure_pattern()
        if pattern:
            reflection["failure_pattern"] = True
            if pattern not in self.failure_alerts_sent:
                reflection["alert_human"] = True
                reflection["key_insight"] = pattern
                self.failure_alerts_sent.add(pattern)
                logger.warning(f"Failure pattern: {pattern}")

        # Store in memory
        self._store_reflection(cycle, reflection)

        logger.info(f"Reflection: score={reflection['score']:.2f}, "
                     f"achieved={reflection['goal_achieved']}, "
                     f"insight={reflection.get('key_insight','')[:60]}")
        return reflection

    def _llm_reflect(self, cycle: CycleResult) -> Optional[Dict]:
        """Use LLM for deep reflection (if budget allows)."""
        prompt = f"""Task: {cycle.task[:200]}
Classification: {cycle.classification}
Plan: {json.dumps(cycle.plan)[:300]}
Result: {str(cycle.result)[:300]}

Evaluate:
1. Score 0-1
2. Key insight
3. Improvements
4. What to remember next time

Output JSON: {{"score":0.0,"key_insight":"...","improvements":[]}}"""
        response = self.llm.reflect(prompt, max_tokens=500)
        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                pass
        return None

    def _detect_failure_pattern(self) -> Optional[str]:
        """Detect recurring failures of same type."""
        if len(self.history) < 3:
            return None

        # Group recent failures (last 10)
        recent = self.history[-10:]
        failures = [c for c in recent if not c.success]
        if len(failures) < 3:
            return None

        # Check if same classification failing
        class_counts: Dict[str, int] = {}
        for f in failures:
            class_counts[f.classification] = class_counts.get(f.classification, 0) + 1

        for cls, count in class_counts.items():
            if count >= 3:
                return f"Failure pattern: {cls} failed {count}/{len(failures)} times"

        return None

    def _store_reflection(self, cycle: CycleResult, reflection: Dict):
        """Store reflection as memory entry."""
        if not self.memory or not hasattr(self.memory, "store"):
            return

        try:
            self.memory.store(
                type="reflection",
                content={
                    "task": cycle.task[:200],
                    "classification": cycle.classification,
                    "score": reflection["score"],
                    "goal_achieved": reflection["goal_achieved"],
                    "key_insight": reflection.get("key_insight", ""),
                    "improvements": reflection.get("improvements", []),
                },
                metadata={
                    "importance": reflection["score"],
                    "source": "reflection",
                    "tags": [cycle.classification, "reflection"],
                }
            )
        except Exception as e:
            logger.debug(f"Memory store failed: {e}")

    def summarize_session(self, n: int = 20) -> str:
        """Generate session summary from recent history."""
        recent = self.history[-n:]
        if not recent:
            return "No activity"

        tasks = [c.task[:80] for c in recent]
        success_rate = sum(1 for c in recent if c.success) / len(recent)
        avg_duration = sum(c.duration_ms for c in recent) / len(recent)

        lines = [
            f"Session: {len(recent)} cycles",
            f"Success rate: {success_rate:.0%}",
            f"Avg duration: {avg_duration:.0f}ms",
            f"Tasks: {', '.join(tasks[:5])}",
        ]

        # Detect if any pattern found
        patterns = list(self.failure_alerts_sent)
        if patterns:
            lines.append(f"Patterns detected: {'; '.join(patterns)}")

        return "\n".join(lines)
