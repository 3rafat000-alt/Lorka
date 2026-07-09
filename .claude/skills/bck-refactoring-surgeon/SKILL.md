---
name: bck-refactoring-surgeon
description: "Technical debt paydown with behavior preservation (characterize-test first)."
---
# Backend - Refactoring Surgeon

Generate PHPUnit characterization tests for legacy code. Snapshots current behavior before refactoring to prevent regressions.

## Tool
`.claude/tools/bck/refactoring-surgeon/characterize-test.sh`

## When to use
- Before refactoring legacy code: capture current behavior in a test
- Gate 4 cleanup: characterize untested code before touching it
- Adding coverage to dead code paths: snapshot what the method does today

## How to use
```bash
.claude/tools/bck/refactoring-surgeon/characterize-test.sh <PRJ-ID> <class-name> <method-name> [test-name]
```

## Input
- `PRJ-ID` — project directory
- `class-name` — fully qualified class name (e.g. `App\\Services\\PaymentService`)
- `method-name` — method to characterize
- `test-name` — optional custom test method name

## Output
- `tests/Feature/{ShortClass}CharacterizationTest.php` — PHPUnit test with:
  - Arrange stub for minimal input
  - Act: calls the target method
  - Assert: non-null and is-array defaults
- Run hint: `php artisan test --filter={testName}`

## Related
- `engine/agents/bck/refactoring-surgeon.md`
- `.claude/tools/bck/refactoring-surgeon/characterize-test.sh`
