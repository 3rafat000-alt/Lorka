"""
SOFI Tool Box — Minimal tool set (4 tools).

Each tool is a callable with name + description + params schema.
LLM uses function-calling style to select tool.
"""

import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("sofi.tools")


@dataclass
class ToolSpec:
    """Tool specification for LLM function calling."""
    name: str
    description: str
    parameters: Dict  # JSON schema
    required: List[str] = field(default_factory=list)
    safety_level: str = "safe"  # safe|medium|critical
    fn: Optional[Callable] = None


@dataclass
class ToolResult:
    success: bool = False
    output: str = ""
    error: str = ""
    duration_ms: float = 0.0


# ── Tool Implementations ─────────────────────────────────────────

class SearchCodeTool:
    """Search project code using grep + semantic search."""

    name = "search_code"
    description = "Search codebase for patterns, functions, or text"
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search term or regex"},
            "file_pattern": {"type": "string", "description": "File glob pattern e.g. *.php", "default": "*"},
            "max_results": {"type": "integer", "description": "Max results", "default": 10},
        }
    }
    required = ["query"]
    safety_level = "safe"

    def __init__(self, project_root: str = "."):
        self.project_root = os.path.abspath(project_root)
        self.exclude_dirs = ["vendor", "node_modules", ".git", "storage", "bootstrap/cache"]

    def __call__(self, query: str, file_pattern: str = "*", max_results: int = 10) -> ToolResult:
        start = time.time()
        try:
            # Build exclude patterns
            exclude_args = []
            for d in self.exclude_dirs:
                exclude_args.extend(["--exclude-dir", d])

            cmd = ["grep", "-rn", "--include=" + file_pattern] + exclude_args + [
                query, self.project_root
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

            output = (result.stdout or result.stderr)[:3000]
            lines = output.split("\n")
            if len(lines) > max_results:
                output = "\n".join(lines[:max_results]) + f"\n... (+{len(lines)-max_results} more)"

            return ToolResult(
                success=result.returncode == 0 or result.returncode == 1,
                output=output or "(no matches)",
                duration_ms=(time.time() - start) * 1000,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Search timed out (>15s)",
                              duration_ms=(time.time() - start) * 1000)
        except Exception as e:
            return ToolResult(success=False, error=str(e),
                              duration_ms=(time.time() - start) * 1000)


class RunTestsTool:
    """Run test suite for specified path."""

    name = "run_tests"
    description = "Run PHPUnit or Pytest tests for given path"
    parameters = {
        "type": "object",
        "properties": {
            "test_path": {"type": "string", "description": "Test file or directory path"},
            "environment": {"type": "string", "enum": ["local", "staging"], "default": "local"},
            "filter": {"type": "string", "description": "Test name filter pattern", "default": ""},
        }
    }
    required = ["test_path"]
    safety_level = "medium"

    def __init__(self, project_root: str = "."):
        self.project_root = os.path.abspath(project_root)

    def __call__(self, test_path: str, environment: str = "local", filter: str = "") -> ToolResult:
        start = time.time()
        try:
            full_path = os.path.join(self.project_root, test_path)
            if not os.path.exists(full_path):
                return ToolResult(success=False, error=f"Path not found: {test_path}",
                                  duration_ms=(time.time() - start) * 1000)

            # Detect test runner
            if os.path.exists(os.path.join(self.project_root, "phpunit.xml")):
                cmd = ["./vendor/bin/phpunit", test_path]
            elif os.path.exists(os.path.join(self.project_root, "pytest.ini")):
                cmd = ["python", "-m", "pytest", test_path, "-x", "-q"]
            elif os.path.exists(os.path.join(self.project_root, "package.json")):
                cmd = ["npx", "jest", test_path, "--no-coverage"]
            else:
                cmd = ["echo", "No test runner detected"]

            if filter:
                cmd.extend(["--filter", filter])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=self.project_root)
            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout[-2000:] or result.stderr[-2000:],
                duration_ms=(time.time() - start) * 1000,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Tests timed out (>120s)",
                              duration_ms=(time.time() - start) * 1000)
        except Exception as e:
            return ToolResult(success=False, error=str(e),
                              duration_ms=(time.time() - start) * 1000)


class CreatePRTool:
    """Create GitHub Pull Request."""

    name = "create_pr"
    description = "Create a pull request on GitHub"
    parameters = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "PR title"},
            "description": {"type": "string", "description": "PR body"},
            "branch": {"type": "string", "description": "Source branch"},
            "base": {"type": "string", "description": "Target branch (default: main)", "default": "main"},
        }
    }
    required = ["title", "branch"]
    safety_level = "critical"

    def __call__(self, title: str, description: str = "", branch: str = "", base: str = "main") -> ToolResult:
        start = time.time()
        try:
            if not branch:
                # Detect current branch
                result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                                        capture_output=True, text=True, timeout=5)
                branch = result.stdout.strip()

            # Create PR via gh CLI
            cmd = ["gh", "pr", "create",
                   "--title", title,
                   "--head", branch,
                   "--base", base]
            if description:
                cmd += ["--body", description]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                logger.info(f"PR created: {result.stdout.strip()}")
            else:
                logger.warning(f"PR failed: {result.stderr}")

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout.strip() or result.stderr.strip(),
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e),
                              duration_ms=(time.time() - start) * 1000)


class SendUpdateTool:
    """Send notification to user/team."""

    name = "send_update"
    description = "Send summary to user via console, slack, or email"
    parameters = {
        "type": "object",
        "properties": {
            "channel": {"type": "string", "enum": ["console", "slack", "email"], "default": "console"},
            "message": {"type": "string", "description": "Message content"},
            "urgency": {"type": "string", "enum": ["low", "medium", "high"], "default": "low"},
        }
    }
    required = ["message"]
    safety_level = "safe"

    def __call__(self, message: str, channel: str = "console", urgency: str = "low") -> ToolResult:
        start = time.time()
        try:
            prefix = f"[SOFI/{urgency.upper()}] "
            full_msg = prefix + message

            if channel == "console":
                print(f"\n{'='*60}\n{full_msg}\n{'='*60}\n")
            elif channel == "slack":
                # Stub — would call Slack API
                logger.info(f"[SLACK] {full_msg}")
            elif channel == "email":
                # Stub — would call email API
                logger.info(f"[EMAIL] {full_msg}")

            logger.info(f"Update sent ({channel}/{urgency}): {message[:60]}...")
            return ToolResult(success=True, output=f"Sent to {channel}",
                              duration_ms=(time.time() - start) * 1000)
        except Exception as e:
            return ToolResult(success=False, error=str(e),
                              duration_ms=(time.time() - start) * 1000)


# ── Tool Box ─────────────────────────────────────────────────────

class ToolBox:
    """Registry of all tools. LLM selects by name."""

    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self._tools: Dict[str, ToolSpec] = {}
        self._register_defaults()

    def _register_defaults(self):
        """Register the 4 core tools."""
        search = SearchCodeTool(self.project_root)
        self.register(ToolSpec(
            name=search.name,
            description=search.description,
            parameters=search.parameters,
            required=search.required,
            safety_level=search.safety_level,
            fn=search,
        ))

        tests = RunTestsTool(self.project_root)
        self.register(ToolSpec(
            name=tests.name,
            description=tests.description,
            parameters=tests.parameters,
            required=tests.required,
            safety_level=tests.safety_level,
            fn=tests,
        ))

        pr = CreatePRTool()
        self.register(ToolSpec(
            name=pr.name,
            description=pr.description,
            parameters=pr.parameters,
            required=pr.required,
            safety_level=pr.safety_level,
            fn=pr,
        ))

        update = SendUpdateTool()
        self.register(ToolSpec(
            name=update.name,
            description=update.description,
            parameters=update.parameters,
            required=update.required,
            safety_level=update.safety_level,
            fn=update,
        ))

    def register(self, spec: ToolSpec):
        self._tools[spec.name] = spec
        logger.info(f"Tool registered: {spec.name} [{spec.safety_level}]")

    def get_specs(self) -> List[Dict]:
        """Return tool specs in function-calling format for LLM."""
        return [
            {
                "name": s.name,
                "description": s.description,
                "parameters": s.parameters,
            }
            for s in self._tools.values()
        ]

    def execute(self, tool_name: str, params: Dict) -> ToolResult:
        """Execute tool by name with params."""
        spec = self._tools.get(tool_name)
        if not spec:
            return ToolResult(success=False, error=f"Unknown tool: {tool_name}")

        if not spec.fn:
            return ToolResult(success=False, error=f"Tool {tool_name} has no handler")

        logger.info(f"Executing: {tool_name}({json.dumps(params)[:100]})")
        try:
            result = spec.fn(**params)
            logger.info(f"Result: {result.output[:100]}... ({result.duration_ms:.0f}ms)")
            return result
        except TypeError as e:
            return ToolResult(success=False, error=f"Invalid params: {e}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())
