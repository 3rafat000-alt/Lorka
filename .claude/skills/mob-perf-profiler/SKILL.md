---
name: mob-perf-profiler
description: "Shrink-wrap and leaks — mandatory before/after measurements."
---
# Mobile - Performance Profiler

Capture before/after performance measurements for Flutter builds. Record baselines, measure app size, compare against historical data, and generate reports.

## Tool
`.claude/tools/mob/perf-profiler/perf-measure.sh`

## When to use
- Gate 4 mobile performance: record baseline before optimization
- Performance regression check: compare current build size against baseline
- Release prep: measure app bundle size before store submission
- CI pipeline: automated perf comparison across builds

## How to use
```bash
.claude/tools/mob/perf-profiler/perf-measure.sh <PRJ-ID> <action> [label]
```

## Input
- `PRJ-ID` — project directory
- `<action>`:
  - `start <label>` — record baseline with current SHA + timestamp
  - `measure` — find and measure APK/AAB size
  - `compare <label>` — compare current against baseline
  - `report` — generate perf report with all baselines
- `label` — baseline identifier (for start/compare)

## Output
- `start`: `_context/perf/baseline-{label}.json` with sha, date, app size
- `measure`: APK/AAB file size in KB
- `compare`: baseline size vs current commit diff
- `report`: markdown report in `_context/perf/report.md`

## Related
- `engine/agents/mob/perf-profiler.md`
- `.claude/tools/mob/perf-profiler/perf-measure.sh`
