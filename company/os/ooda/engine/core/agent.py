"""
SOFI Main Agent — Async OODA loop.

Event-driven, no polling. Each cycle:
  1. await event from EventBus
  2. Classify (keyword)
  3. Retrieve context (vector memory)
  4. Plan (LLM)
  5. Execute tool(s)
  6. Reflect (score + memory)
  7. Send summary if needed
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .memory import VectorMemory
from .perception import EventBus, Event
from .reasoning import ReasoningEngine, Decision, ContextCompressor
from .reflection import ReflectionEngine, CycleResult
from ..tools.toolbox import ToolBox, ToolResult

logger = logging.getLogger("sofi.agent")


class SOFIAgent:
    """Autonomous agent with token-efficient OODA loop.

    1. EventBus -> Event
    2. Classify (no LLM)
    3. Retrieve memory (vector + keyword hybrid)
    4. Compress context (truncate + summarize)
    5. Plan (LLM — cheapest model possible)
    6. Execute tool(s)
    7. Reflect + store in memory
    8. Optional: send summary
    """

    def __init__(self, config: Dict, project_root: str = "."):
        self.config = config
        self.project_root = project_root
        self.agent_id = config.get("agent", {}).get("id", "sofi-default")
        self.project_id = config.get("agent", {}).get("project_id", "default")
        self.verbose = config.get("logging", {}).get("level", "INFO") == "DEBUG"

        # Core modules
        self.memory = VectorMemory(config)
        self.event_bus = EventBus()
        self.toolbox = ToolBox(project_root)
        self.llm = self._init_llm()
        self.reasoning = ReasoningEngine(self.memory, self.llm, config)
        self.reflection = ReflectionEngine(self.memory, self.llm)
        self.compressor = ContextCompressor()

        # Stats
        self.cycle_count = 0
        self.start_time = time.time()
        self.last_summary_time = 0
        self.summary_interval = config.get("agent", {}).get("summary_interval_seconds", 3600)

        # Reporting
        logger.info(f"SOFI Agent ready — {self.agent_id}")
        logger.info(f"Tools: {', '.join(self.toolbox.list_tools())}")
        logger.info(f"Memory backend: {config.get('memory', {}).get('backend', 'chroma')}")
        logger.info(f"Daily token budget: {config.get('reasoning', {}).get('daily_token_limit', 100000)}")

    def _init_llm(self) -> Optional[Any]:
        """Initialize LLM client, or a stub with an explicit warning if unavailable."""
        try:
            import anthropic
        except ImportError:
            logger.warning("anthropic SDK not installed — using STUB LLM (no real inference). "
                           "`pip install anthropic` and restart.")
            return _StubLLM()
        # SDK resolves credentials from ANTHROPIC_API_KEY → ANTHROPIC_AUTH_TOKEN → `ant auth login` profile.
        if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
            logger.warning("No ANTHROPIC_API_KEY/ANTHROPIC_AUTH_TOKEN in env — using STUB LLM (no real "
                           "inference). Set a key or run `ant auth login`, then restart.")
            return _StubLLM()
        client = anthropic.Anthropic()  # zero-arg: picks up key/token from env
        logger.info("LLM: Anthropic client ready")
        return _LLMWrapper(client, self.config.get("llm", {}))

    async def run(self):
        """Main OODA loop — event-driven, no polling."""
        logger.info("OODA loop started (event-driven)")

        # Load initial context from project files
        self._load_project_context()

        async for event in self.event_bus.stream():
            self.cycle_count += 1
            try:
                await self._process_event(event)
            except Exception as e:
                logger.error(f"Cycle {self.cycle_count} failed: {e}", exc_info=self.verbose)

            # Periodic summary
            if time.time() - self.last_summary_time > self.summary_interval:
                self._send_summary()
                self.last_summary_time = time.time()

    async def _process_event(self, event: Event):
        """Process single event through full OODA cycle."""
        t_start = time.time()
        logger.info(f"─── Cycle {self.cycle_count}: [{event.source}] {event.summary[:60]} ───")

        # Step 1: CLASSIFY (keyword-based, no LLM)
        dec = self.reasoning.classify(event.summary + " " + json.dumps(event.raw)[:200], event.source)

        # Step 2: RETRIEVE MEMORY (hybrid search)
        memories = []
        if hasattr(self.memory, "retrieve"):
            try:
                memories = self.memory.retrieve(
                    event.summary,
                    k=5,
                    min_importance=0.3
                )
            except Exception:
                pass

        # Step 3: COMPRESS CONTEXT
        compressed = self.compressor.compress(
            [{"type": m.type, "content": m.content, "metadata": m.metadata}
             for m in memories] if memories else [],
            event.summary,
            max_tokens=1500
        )

        # Step 4: PLAN (if needs planning)
        if dec.complexity >= 0.3:
            dec = self.reasoning.create_plan(
                f"[{event.source}/{event.type}] {event.summary}",
                compressed,
                dec
            )

        # Step 5: EXECUTE TOOL
        tool_results = []
        for step in dec.plan:
            # Parse tool call from plan step
            tool_name, params = self._parse_step(step, event)
            if tool_name == "none":
                continue

            result = self.toolbox.execute(tool_name, params)
            tool_results.append(result)

            if not result.success and dec.needs_approval:
                logger.warning(f"Tool failed + needs approval: {tool_name}")
                self.toolbox.execute("send_update", {
                    "message": f"Action '{tool_name}' failed: {result.error}",
                    "urgency": "high",
                })
                break

        # Step 6: REFLECT
        cycle_result = CycleResult(
            task=event.summary,
            classification=dec.classification,
            plan=dec.plan,
            tool_calls=[{"name": t, "success": r.success}
                       for t, r in zip(dec.plan, tool_results)] if tool_results else [],
            result=[r.output for r in tool_results if r.success] if tool_results else "no_action",
            duration_ms=(time.time() - t_start) * 1000,
            success=all(r.success for r in tool_results) if tool_results else True,
        )
        reflection = self.reflection.evaluate(cycle_result)

        # Step 7: ALERT ON FAILURE PATTERN
        if reflection.get("alert_human"):
            self.toolbox.execute("send_update", {
                "message": f"⚠️ {reflection.get('key_insight', 'Failure pattern detected')}",
                "channel": "console",
                "urgency": "high",
            })

        # Log budget info
        remaining = self.reasoning.budget.remaining()
        if remaining < self.reasoning.budget.daily_limit * 0.2:
            logger.info(f"Budget: {remaining}/{self.reasoning.budget.daily_limit} remaining")

    def _parse_step(self, step: str, event: Event) -> tuple:
        """Parse plan step into (tool_name, params)."""
        step_lower = step.lower()

        # Heuristic tool matching
        if "search" in step_lower or "find" in step_lower or "grep" in step_lower:
            return "search_code", {"query": event.summary, "max_results": 10}
        elif "test" in step_lower or "phpunit" in step_lower or "pytest" in step_lower:
            return "run_tests", {"test_path": ".", "environment": "local"}
        elif "pr" in step_lower or "pull" in step_lower or "merge" in step_lower:
            return "create_pr", {"title": event.summary[:72], "branch": f"fix/{event.id[:8]}"}
        elif "notify" in step_lower or "send" in step_lower or "update" in step_lower or "alert" in step_lower:
            return "send_update", {"message": event.summary, "channel": "console", "urgency": "medium"}
        else:
            return "none", {}

    def _load_project_context(self):
        """Load SOFI project context files into memory."""
        # Try relative path (symlink) first, then absolute
        context_paths = [
            f"projects/{self.project_id}/_context",
            os.path.join(os.path.expanduser("~"), "Desktop", "projects", self.project_id, "_context"),
        ]
        for context_dir in context_paths:
            if os.path.isdir(context_dir):
                break
        else:
            logger.warning(f"Context dir not found for {self.project_id}")
            return

        for fname in ["STATE.md", "CONTEXT.md", "HANDOFFS.md"]:
            path = os.path.join(context_dir, fname)
            if os.path.exists(path):
                try:
                    with open(path) as f:
                        content = f.read()[:2000]
                    if hasattr(self.memory, "store"):
                        self.memory.store(
                            type="context",
                            content={"file": fname, "content": content},
                            metadata={"project": self.project_id, "importance": 0.8,
                                      "source": "file", "tags": ["context", "project"]}
                        )
                except Exception as e:
                    logger.debug(f"Failed to load {fname}: {e}")

    def _send_summary(self):
        """Send periodic session summary."""
        summary = self.reflection.summarize_session(20)
        elapsed = time.time() - self.start_time
        hours = elapsed / 3600
        summary += f"\nUptime: {hours:.1f}h, Cycles: {self.cycle_count}"

        self.toolbox.execute("send_update", {
            "message": summary,
            "channel": "console",
            "urgency": "low",
        })

    def stop(self):
        """Graceful shutdown."""
        self.event_bus.stop()
        logger.info("SOFI Agent stopped")


class _LLMWrapper:
    """Wrapper for Anthropic API with model routing."""

    def __init__(self, client: Any, config: Dict):
        self.client = client
        self.models = {
            "haiku": config.get("fast", {}).get("model", "claude-haiku-4-5"),
            "sonnet": config.get("reasoning", {}).get("model", "claude-sonnet-4-6"),
            "opus": config.get("opus", {}).get("model", "claude-opus-4-8"),
        }

    def _call(self, model_key: str, prompt: str, system: str = "", max_tokens: int = 2000) -> str:
        model = self.models.get(model_key, self.models["haiku"])
        try:
            response = self.client.messages.create(
                model=model,
                system=system or None,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"LLM call failed ({model_key}): {e}")
            return f""

    def reason(self, prompt: str, system: str = "") -> str:
        return self._call("sonnet", prompt, system, 4096)

    def fast(self, prompt: str, system: str = "") -> str:
        return self._call("haiku", prompt, system, 1500)

    def reflect(self, prompt: str, max_tokens: int = 500) -> str:
        return self._call("haiku", prompt, max_tokens=max_tokens)


class _StubLLM:
    """Stub LLM for testing without API key."""

    def reason(self, prompt: str, system: str = "") -> str:
        return json.dumps({"goal": "stub", "steps": [{"step": 1, "action": "search_code",
                                                       "tool": "search_code", "params": {"query": "test"}}],
                           "needs_approval": False, "estimated_tokens": 500})

    def fast(self, prompt: str, system: str = "") -> str:
        return json.dumps({"classification": "routine", "confidence": 0.8,
                           "complexity": 0.3, "needs_approval": False, "reasoning": "stub"})

    def reflect(self, prompt: str, max_tokens: int = 500) -> str:
        return json.dumps({"score": 0.7, "goal_achieved": True, "key_insight": "stub reflection",
                           "improvements": [], "failure_pattern": False, "alert_human": False})
