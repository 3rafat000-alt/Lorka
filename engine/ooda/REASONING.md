# Layer 3: Reasoning & Planning — Thinking and Planning

> The cognitive core. Three modes: ReAct (default), Plan-and-Execute (complex), Reflexion (self-improving).

## Three Reasoning Modes

```
┌────────────────────────────────────────────────────────┐
│                    REASONING ENGINE                      │
├──────────────┬───────────────────┬─────────────────────┤
│   ReAct      │  Plan-Execute     │   Reflexion          │
│  (default)   │  (complex tasks)  │   (self-improving)   │
├──────────────┼───────────────────┼─────────────────────┤
│ Think→Act→   │ Plan→Execute→     │ Think→Act→Reflect→  │
│ Think→Act→   │   subtasks         │   Learn→Think→Act→  │
│   (loop)     │                   │     (continuous)     │
├──────────────┼───────────────────┼─────────────────────┤
│ Single-step  │ Multi-step        │ +Self-evaluation     │
│ quick tasks  │ projects          │ +Pattern detection   │
│              │                   │ +Strategy adjustment │
└──────────────┴───────────────────┴─────────────────────┘
```

## Mode Selection

| Task Complexity | Duration | Mode |
|----------------|----------|------|
| Simple reply, single edit | < 5 min | ReAct |
| Feature implementation, bug fix | 5–60 min | ReAct + Reflexion |
| Multi-file refactor, new module | 1–4 hours | Plan-Execute + Reflexion |
| Architecture, design, strategy | > 4 hours | Plan-Execute + Human-in-loop |

## ReAct (Reasoning + Acting)

```
Thought: The user needs their password reset. I need to verify identity first.
Action: search("user identity verification policy")
Observation: Policy requires security question + email confirmation.
Thought: I'll ask the security questions, then trigger email.
Action: send_message("user", "Answer your security question:")
...
```

**SOFI Protocol**:
```
Observation → Memory → [Thought → Tool → Observation]ⁿ → Decision → Execution → Reflection
```

## Plan-and-Execute

For complex tasks, SOFI:
1. **Decomposes**: breaks task into DAG of subtasks (dependency graph)
2. **Plans**: assigns each subtask to appropriate agent/tool
3. **Executes**: runs subtasks with parallelization where possible
4. **Monitors**: checks progress, re-plans on failure
5. **Evaluates**: assesses if plan achieved goal

```python
def plan_and_execute(self, task: str) -> Result:
    plan = self.llm.decompose(task)  # list of subtasks with deps
    graph = build_dag(plan)
    
    results = {}
    for batch in topological_sort(graph):
        parallel_results = parallel_map(self.execute_subtask, batch)
        results.update(parallel_results)
        
        # Check if re-planning needed
        if any(r.failed for r in parallel_results):
            plan = self.llm.replan(task, results)
            graph = build_dag(plan)
    
    return self.evaluate(task, results)
```

## Reflexion (Self-Improving)

After each action cycle:

```python
def reflect(self, observation, action, result):
    evaluation = self.llm.evaluate({
        "goal": observation.parsed.intent,
        "action": action,
        "result": result,
        "criteria": ["accuracy", "efficiency", "completeness"]
    })
    
    if evaluation.score < 0.7:
        # What went wrong? Store as learning
        self.memory.store({
            "type": "failure_pattern",
            "context": observation,
            "action": action,
            "error": evaluation.error_analysis,
            "improvement": evaluation.suggested_change
        })
        
        # Try again with improved approach
        improved_action = self.llm.improve(action, evaluation)
        return self.execute(improved_action)
    
    # Store successful pattern
    self.memory.store({
        "type": "success_pattern",
        "context": observation.fingerprint,
        "action": action,
        "result_summary": evaluation.summary
    })
```

## Chain of Thought (CoT)

SOFI uses structured CoT for every reasoning step:

```
┌─────────────────────────────────────────┐
│ 1. SITUATION: What do I observe?        │
│ 2. GOAL: What needs to be achieved?     │
│ 3. CONSTRAINTS: What limits exist?      │
│ 4. OPTIONS: What approaches could work? │
│ 5. DECISION: Best option + why          │
│ 6. ACTION: What I will do now           │
│ 7. EXPECTATION: What should happen      │
│ 8. VERIFICATION: Did it work?           │
└─────────────────────────────────────────┘
```

## Human-in-the-Loop

| Confidence | Decision Type | Action |
|-----------|--------------|--------|
| > 0.9 | Code, non-critical | Auto-execute |
| > 0.7 | Config change, reply | Auto, log for review |
| > 0.5 | State mutation, deploy | Propose, wait for approval |
| < 0.5 | Any significant change | Propose with reasoning, wait |
