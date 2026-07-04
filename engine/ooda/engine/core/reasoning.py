"""
SOFI Reasoning Engine — Classification, Planning, Model Routing.

Decision Tree:
1. Classify problem (bug|feature|question|urgent|routine)
2. Retrieve context from memory
3. Plan (ReAct | Plan-Execute | Reflexion)
4. Risk assessment (needs approval?)
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("sofi.reasoning")


# ── Reasoning Modes ──────────────────────────────────────────────

class ReasoningMode(Enum):
    REACT = "react"
    PLAN_EXECUTE = "plan_execute"
    REFLEXION = "reflexion"


class Complexity(Enum):
    TRIVIAL = 0.2   # Haiku — classification, summarization
    SIMPLE = 0.4    # Haiku — formatting, extraction
    MODERATE = 0.6  # Sonnet — planning, code writing
    COMPLEX = 0.8   # Sonnet — debugging, architecture
    CRITICAL = 1.0  # Opus — security, production decisions


# ── Decision Output ──────────────────────────────────────────────

@dataclass
class Decision:
    """Structured output from reasoning."""
    classification: str = ""        # bug|feature|question|urgent|routine
    confidence: float = 0.0         # 0.0–1.0
    complexity: float = 0.0         # 0.0–1.0
    model: str = "haiku"            # routed model
    plan: List[str] = field(default_factory=list)
    needs_approval: bool = False
    reasoning: str = ""
    estimated_tokens: int = 0


# ── Model Router ─────────────────────────────────────────────────

class ModelRouter:
    """Route tasks to cheapest capable model.

    haiku ($0.25/M input) — classification, format, summarize
    sonnet ($3/M input)   — planning, coding, analysis
    opus ($15/M input)    — critical, security, architecture
    """

    MODEL_COST = {
        "haiku": 0.25,
        "sonnet": 3.00,
        "opus": 15.00,
    }

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

    def route(self, complexity: float) -> str:
        if complexity < 0.3:
            return "haiku"
        elif complexity < 0.7:
            return "sonnet"
        else:
            return "opus"

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int = 1000) -> float:
        cost_per_m = self.MODEL_COST.get(model, 3.0)
        return (input_tokens + output_tokens) / 1_000_000 * cost_per_m


# ── Token Budget ─────────────────────────────────────────────────

class TokenBudget:
    """Daily token budget with economy mode.

    hard_limit: absolute max tokens/day -> switch to haiku-only
    soft_limit: warning threshold
    """

    def __init__(self, daily_limit: int = 100_000):
        self.daily_limit = daily_limit
        self.used_today = 0
        self.date = datetime.now(timezone.utc).date()
        self.economy_mode = False

    def check(self, estimated: int = 0) -> str:
        """Returns 'normal' | 'economy' | 'blocked'."""
        self._rotate_date()

        if self.used_today + estimated > self.daily_limit:
            self.economy_mode = True
            logger.warning(f"Token budget exceeded ({self.used_today}/{self.daily_limit}). Economy mode.")
            return "economy"

        if self.used_today > self.daily_limit * 0.8:
            logger.info(f"Token budget at {self.used_today}/{self.daily_limit} — near limit")
            return "economy"  # be conservative

        return "normal"

    def spend(self, tokens: int):
        self._rotate_date()
        self.used_today += tokens

    def _rotate_date(self):
        today = datetime.now(timezone.utc).date()
        if today != self.date:
            self.used_today = 0
            self.economy_mode = False
            self.date = today
            logger.info(f"Token budget reset for {today}")

    def remaining(self) -> int:
        self._rotate_date()
        return max(0, self.daily_limit - self.used_today)


# ── Context Compressor ───────────────────────────────────────────

class ContextCompressor:
    """Compress memories before LLM call. Reduces context by ~60%."""

    def compress(self, memories: List[Dict], query: str, max_tokens: int = 2000) -> str:
        """Take list of memory dicts, return compressed context string."""
        if not memories:
            return ""

        # 1. Sort by importance then relevance
        scored = []
        for m in memories:
            importance = m.get("metadata", {}).get("importance", 0.5)
            summary = m.get("content", {}).get("summary", str(m.get("content", ""))[:200])
            scored.append((importance, summary, m))

        scored.sort(key=lambda x: x[0], reverse=True)

        # 2. Take top 5, truncate each to 200 chars
        parts = []
        token_est = 0
        for imp, summary, mem in scored[:5]:
            truncated = summary[:200]
            entry = f"[{mem.get('type','?')}][{imp:.1f}] {truncated}"
            entry_tokens = len(entry) // 4  # rough estimate
            if token_est + entry_tokens > max_tokens:
                break
            parts.append(entry)
            token_est += entry_tokens

        return "\n".join(parts) if parts else "(no relevant context)"


# ── System Prompts (compressed) ──────────────────────────────────

SYSTEM_PROMPT = """
SOFI: autonomous agent. Rules:
1. prod=ask_approval
2. confidence<0.7=escalate
3. auto:docs,tests,minor_fixes
4. notify:daily_summary
5. budget:economy if >80% daily limit
User: fast>perfect, hates_repetition, bilingual ar/en
"""

CLASSIFIER_PROMPT = """
Classify task. Output JSON:
{"classification":"bug|feature|question|urgent|routine",
"confidence":0.0-1.0,"complexity":0.0-1.0,
"needs_approval":bool,"reasoning":"..."}
"""

PLANNER_PROMPT = """
Plan steps. Max 5. Output JSON:
{"goal":"...","steps":[{"step":1,"action":"...","tool":"...","params":{}}],
"needs_approval":bool,"estimated_tokens":int}
"""

REFLECTOR_PROMPT = """
Evaluate result. Output JSON:
{"score":0.0-1.0,"goal_achieved":bool,"key_insight":"...",
"improvements":[],"failure_pattern":bool,"alert_human":bool}
"""


# ── Reasoning Engine ─────────────────────────────────────────────

class ReasoningEngine:
    """Core cognition: classify -> context -> plan -> risk."""

    def __init__(self, memory: Any, llm: Any, config: Optional[Dict] = None):
        self.memory = memory
        self.llm = llm
        self.config = config or {}
        self.router = ModelRouter()
        self.budget = TokenBudget(daily_limit=config.get("daily_token_limit", 100_000))
        self.compressor = ContextCompressor()
        self.complexity_keywords = {
            "bug": 0.5, "refactor": 0.6, "deploy": 0.9,
            "security": 1.0, "summarize": 0.2, "plan": 0.7,
            "design": 0.8, "test": 0.4, "docs": 0.2,
            "review": 0.5, "search": 0.3,
        }

    def classify(self, task: str, source: str = "") -> Decision:
        """Step 1: Classify problem type and complexity."""
        dec = Decision(classification="routine", confidence=0.5, complexity=0.3)

        # Fast keyword-based classification (no LLM call)
        task_lower = task.lower()

        if any(w in task_lower for w in ["bug", "error", "fail", "crash", "wrong"]):
            dec.classification = "bug"
            dec.complexity = 0.6
        elif any(w in task_lower for w in ["feature", "add ", "new ", "create", "implement"]):
            dec.classification = "feature"
            dec.complexity = 0.6
        elif any(w in task_lower for w in ["question", "how", "what", "why", "help"]):
            dec.classification = "question"
            dec.complexity = 0.3
        elif any(w in task_lower for w in ["urgent", "asap", "critical", "production", "down"]):
            dec.classification = "urgent"
            dec.complexity = 0.9
            dec.needs_approval = True
        else:
            dec.classification = "routine"
            dec.complexity = 0.3

        # Refine with keyword matching
        for kw, comp in self.complexity_keywords.items():
            if kw in task_lower:
                dec.complexity = max(dec.complexity, comp)

        # Route to model
        dec.confidence = min(0.5 + dec.complexity * 0.4, 0.95)
        dec.model = self.router.route(dec.complexity)

        # Budget check
        budget_status = self.budget.check(2000)
        if budget_status == "economy":
            dec.model = "haiku"  # Force cheapest
        elif budget_status == "blocked":
            dec.model = "haiku"
            dec.confidence = min(dec.confidence, 0.5)

        # Production check
        if any(w in task_lower for w in ["production", "prod", "deploy", "live"]):
            dec.needs_approval = True

        logger.info(f"Classified: {dec.classification} (c={dec.complexity:.1f}, "
                     f"model={dec.model}, approval={dec.needs_approval})")
        return dec

    def create_plan(self, task: str, context: str, dec: Decision) -> Decision:
        """Step 3: Create execution plan using appropriate model."""
        if dec.complexity < 0.3:
            # Trivial — plan is just "do it"
            dec.plan = [f"Execute: {task[:100]}"]
            dec.estimated_tokens = 500
            return dec

        # Retrieve relevant memories
        memories = []
        if hasattr(self.memory, "retrieve"):
            try:
                memories = self.memory.retrieve(task, k=5, min_importance=0.3)
            except Exception:
                pass

        # Compress context
        compressed_ctx = self.compressor.compress(
            [{"type": m.type, "content": m.content, "metadata": m.metadata}
             for m in memories] if memories else [],
            task,
            max_tokens=1500
        )

        # Build prompt
        prompt = f"""Task: {task[:500]}
Context: {compressed_ctx[:1500]}
{PLANNER_PROMPT}"""

        # Call LLM (use model from classification)
        response = ""
        if self.llm:
            try:
                model_map = {"haiku": "fast", "sonnet": "reason", "opus": "reason"}
                method = model_map.get(dec.model, "reason")
                if hasattr(self.llm, method):
                    response = getattr(self.llm, method)(prompt, SYSTEM_PROMPT)
            except Exception as e:
                logger.error(f"LLM plan failed: {e}")

        if response:
            try:
                data = json.loads(response)
                dec.plan = [s.get("action", "") for s in data.get("steps", [])]
                dec.needs_approval = dec.needs_approval or data.get("needs_approval", False)
                dec.estimated_tokens = data.get("estimated_tokens", 2000)
            except json.JSONDecodeError:
                dec.plan = [response[:200]]

        if not dec.plan:
            dec.plan = [f"Process: {task[:100]}"]

        logger.info(f"Plan: {len(dec.plan)} steps, model={dec.model}, "
                     f"approval={dec.needs_approval}")
        return dec

    def reflect(self, task: str, plan: List[str], result: Any) -> Dict:
        """Step 5: Evaluate result and extract learnings."""
        prompt = f"""Task: {task[:300]}
Plan: {json.dumps(plan)[:500]}
Result: {str(result)[:500]}
{REFLECTOR_PROMPT}"""

        response = ""
        if self.llm and hasattr(self.llm, "reflect"):
            try:
                response = self.llm.reflect(prompt)
            except Exception as e:
                logger.error(f"Reflection failed: {e}")

        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                pass

        # Default reflection
        return {
            "score": 0.5,
            "goal_achieved": False,
            "key_insight": "Reflection parsing failed",
            "improvements": ["Improve result capture"],
            "failure_pattern": False,
            "alert_human": False,
        }

    def detect_failure_pattern(self, recent_results: List[Dict]) -> Optional[str]:
        """Check if same task type failing repeatedly."""
        if len(recent_results) < 3:
            return None

        failures = [r for r in recent_results[-5:] if r.get("score", 0.5) < 0.4]
        if len(failures) >= 3:
            types = [r.get("classification", "?") for r in failures]
            logger.warning(f"Failure pattern detected: {types}")
            return f"Recurring failures in: {', '.join(set(types))}"
        return None
