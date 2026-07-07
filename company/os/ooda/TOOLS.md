# Layer 4: Tool Use — Tool Box

> Every capability SOFI has is a registered tool. Tools are discoverable, sandboxed, and audited.

## Architecture

```
┌─────────────────────────────────────────────┐
│              TOOL REGISTRY                    │
├──────────────┬──────────────┬────────────────┤
│   Code       │  Comm        │  Analytics      │
│   Tools      │  Tools       │  Tools          │
├──────────────┼──────────────┼────────────────┤
│ • Git (CRUD) │ • Slack      │ • SQL Query     │
│ • File I/O   │ • Email      │ • Data Viz      │
│ • Shell      │ • Discord    │ • Report Gen    │
│ • Sandbox    │ • Notify     │ • Log Analysis  │
├──────────────┼──────────────┼────────────────┤
│   Search     │  Deploy      │  Admin          │
│   Tools      │  Tools       │  Tools          │
├──────────────┼──────────────┼────────────────┤
│ • Web Search │ • Deploy Env │ • Config Set    │
│ • Code Search│ • Rollback   │ • User Mgmt     │
│ • Doc Search │ • Health Ck  │ • Permission    │
│ • Vector DB  │ • Scale      │ • Audit Log     │
└──────────────┴──────────────┴────────────────┘
```

## Tool Schema

Each tool registers with:

```json
{
  "name": "git_commit",
  "description": "Stage files and commit with message",
  "category": "code",
  "sandbox": "required",
  "parameters": {
    "files": {"type": "array", "items": "string", "description": "Files to stage"},
    "message": {"type": "string", "description": "Commit message"}
  },
  "returns": {
    "type": "object",
    "properties": {
      "commit_hash": {"type": "string"},
      "success": {"type": "boolean"}
    }
  },
  "danger_level": "medium",
  "requires_approval": false,
  "rate_limit": "10/min"
}
```

## Safety Levels

| Level | Description | Examples | Action |
|-------|-------------|----------|--------|
| safe | Read-only, no side effects | Search, Read, SQL SELECT | Auto |
| low | Non-destructive writes | Log, Notify, Create branch | Auto |
| medium | State mutation | Commit, Deploy, SQL INSERT | Log + alert |
| high | Destructive | Delete, Drop table, Rollback | Require approval |
| critical | Production impact | Prod deploy, DB migration, Config change | Human-in-loop |

## Sandbox

All `medium+` tools execute inside an isolated sandbox: no network access, read-only root, capability-dropped, scoped to a shared workspace mount.

## Tool Discovery

SOFI discovers available tools at startup:

```python
class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self._load_builtins()
        self._load_custom()
    
    def find(self, task: str) -> List[Tool]:
        """LLM-based tool selection from task description."""
        task_embedding = self.embed(task)
        candidates = self.vector_index.similarity_search(task_embedding, k=5)
        return self.llm.select_tools(task, candidates)
    
    def execute(self, tool_name: str, params: dict) -> Result:
        tool = self.tools[tool_name]
        if tool.danger_level >= "high":
            self._request_approval(tool, params)
        return self._sandboxed_execute(tool, params)
```

## Audit Trail

Every tool call is logged:

```json
{
  "tool": "git_commit",
  "params": {"files": ["fix.php"], "message": "fix: auth bug"},
  "timestamp": "ISO8601",
  "agent": "sofi-backend-dev",
  "duration_ms": 1200,
  "result": "success",
  "approval": "auto",
  "trace_id": "trace_<ulid>"
}
```

## Custom Tools

Tools are extensible. The live engine (v2) registers tools on the **`ToolBox`**
(`company/os/ooda/engine/tools/toolbox.py`), wired by `company/os/ooda/engine/core/agent.py`. A tool is a callable exposing
`name`/`description`/`parameters` (JSON schema) plus a `safety_level` (`safe|medium|critical`),
registered as a `ToolSpec`:

```python
# add to company/os/ooda/engine/tools/toolbox.py
from sofi.ooda.engine.tools.toolbox import ToolSpec, ToolResult

class MyCustomTool:
    name = "my_tool"
    description = "Does something specific"
    parameters = {"type": "object", "properties": {
        "target": {"type": "string", "description": "what to act on"},
    }}
    required = ["target"]
    safety_level = "safe"  # safe | medium | critical

    def __init__(self, project_root: str = "."):
        self.project_root = project_root

    def __call__(self, target: str) -> ToolResult:
        return ToolResult(success=True, output=f"done: {target}")

# register it (in ToolBox._register_defaults, or after construction):
tool = MyCustomTool(project_root)
toolbox.register(ToolSpec(
    name=tool.name, description=tool.description,
    parameters=tool.parameters, required=tool.required,
    safety_level=tool.safety_level, fn=tool,
))
```
