---
name: ops-cicd-engineer
description: "Lint→test→build→scan→deploy pipeline — gated green + approval."
---
# Operations - CI/CD Engineer

Generate CI pipeline config (lint → test → build → scan → deploy).

## Tool
`.claude/tools/ops/cicd-engineer/pipeline-gen.sh`

## When to use
- New project scaffold — first CI setup
- Switching CI provider (GitHub → GitLab)
- Adding deploy stage to existing pipeline
- Standardizing pipeline pattern across projects

## How to use
```bash
.claude/tools/ops/cicd-engineer/pipeline-gen.sh --prj PRJ-XXXX [--stack php|python|node|flutter] [--provider github|gitlab] [--output .github/workflows/ci.yml]
```

## Input
PRJ-ID. Auto-detects stack from composer.json/requirements.txt/package.json/pubspec.yaml. Defaults to GitHub Actions.

## Output
Writes CI pipeline YAML to project. Stages: lint, type check, test, build, security scan, deploy.

## Related
- `engine/agents/ops/ops-cicd-engineer.md`
- `.claude/tools/ops/cicd-engineer/pipeline-gen.sh`
