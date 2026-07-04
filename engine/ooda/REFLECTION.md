# Layer 5: Reflection & Learning — Reflection and Learning

> The metacognitive layer. SOFI evaluates itself after every cycle and stores the lessons.

## Reflection Loop

```
After every OODA cycle:
1. SELF-EVALUATE: Did I achieve the goal?
2. ERROR ANALYSIS: What went wrong (if anything)?
3. PATTERN DETECTION: Is this a recurring situation?
4. STRATEGY ADJUSTMENT: Should I change approach?
5. MEMORY STORE: Save what I learned
6. METRIC UPDATE: Update success/failure counters
```

## Evaluation Criteria

| Criterion | Weight | Measure |
|-----------|--------|---------|
| Goal achievement | 0.4 | Did the output match intent? |
| Efficiency | 0.2 | Tokens used, tools called, time spent |
| Correctness | 0.2 | No errors, no regressions |
| Completeness | 0.1 | All sub-tasks done? |
| Proactivity | 0.1 | Did SOFI anticipate needs? |

## Scoring

```
Score = Σ(weight × score) for each criterion

> 0.85 → Excellent: store as exemplar
0.70–0.85 → Good: log success pattern
0.50–0.70 → Needs improvement: store failure + suggested fix
< 0.50 → Failed: trigger human review + full analysis
```

## Learning Types

### 1. Failure Learning
```python
def learn_from_failure(self, cycle):
    analysis = self.llm.analyze_failure({
        "context": cycle.observation,
        "action_taken": cycle.action,
        "result": cycle.result,
        "expected": cycle.expectation
    })
    
    self.memory.store({
        "type": "failure",
        "context_fingerprint": cycle.fingerprint,
        "what_went_wrong": analysis.root_cause,
        "how_to_fix": analysis.suggested_fix,
        "prevention": analysis.prevention_tip,
        "severity": analysis.severity
    })
```

### 2. Pattern Recognition
Every 10 cycles, SOFI clusters recent memories to detect patterns:

```python
def detect_patterns(self):
    recent = self.memory.recent(100)
    clusters = self.llm.cluster(recent, max_groups=5)
    
    for cluster in clusters:
        if cluster.size > 3:  # recurring pattern
            self.memory.store({
                "type": "pattern",
                "signal": cluster.common_theme,
                "frequency": cluster.size,
                "recommended_automation": cluster.suggested_action
            })
```

### 3. Preference Learning
SOFI tracks what the user approves/rejects:

| User Action | Signal | Update |
|------------|--------|--------|
| Approved deploy | +confidence | Lower threshold for similar deploys |
| Rejected change | -confidence | Add constraint to similar proposals |
| Manual edit after SOFI | style-preference | Adjust code style in memory |
| Direct instruction | priority-update | Boost similar task priority |

## Periodic Deep Reflections

| Frequency | Type | What happens |
|-----------|------|-------------|
| Every cycle | Light | Score + store + continue |
| Every 10 cycles | Pattern | Cluster + detect patterns |
| Every 24 hours | Consolidation | Merge, prune, summarize |
| Every 7 days | Strategic | Review goals, adjust strategy |
| Every 30 days | Retrospective | Full analysis, update system prompt |

## 7-Day Strategic Reflection

```python
def strategic_reflection(self):
    weekly_memories = self.memory.last_days(7)
    
    analysis = self.llm.strategic_review({
        "accomplished": weekly_memories.success_count,
        "failed": weekly_memories.failure_count,
        "key_decisions": weekly_memories.important_entries,
        "patterns": self.detect_patterns(),
        "user_satisfaction": self._estimate_satisfaction()
    })
    
    self.system_prompt_adjustments = analysis.suggested_prompt_updates
    self.strategy_adjustments = analysis.strategy_changes
    self.focus_areas = analysis.next_week_focus
```

## Reflection Output Schema

```json
{
  "cycle_id": "cycle_<ulid>",
  "score": 0.82,
  "goal_achieved": true,
  "key_insight": "User prefers verbose error messages with Arabic translations",
  "improvements": [
    "Add Arabic translation to all error messages",
    "Use more descriptive variable names"
  ],
  "memory_updates": [
    {"type": "preference", "key": "error_style", "value": "arabic_verbose"}
  ],
  "action_items": [
    "Create Arabic error message template"
  ]
}
```
