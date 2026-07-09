# 📦 Git Discipline

## Spine

Git is the spine. Every session: orient → work → checkpoint → handoff.

## Orient

```bash
sofi sync <PRJ>           # git pull + status
git log --oneline -8      # See last sessions
```

## Checkpoint

```bash
sofi checkpoint <PRJ> "<type>(<scope>): <subject>"
```

Commit early/often. Never hold >1 artifact uncommitted. An uncommitted session is invisible to the next.

## Branch

- `main` — doctrine and protocol changes
- `prj/<ID>` — project work
- Parallel squads use worktrees

## Blocked

| Command | Why |
|---------|-----|
| `git reset --hard` | Hook-blocked. Destroys history. |
| `git push --force` | Hook-blocked. Destroys history. |
| Secrets in history | Hook-scanned. Rejected. |
| `_scratch/` in commit | Hook-scanned. Rejected. |

## Handoff

Every handoff records `head_sha` in STATE.md. The next agent starts on that exact commit.
