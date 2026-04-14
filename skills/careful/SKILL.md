---
name: careful
version: 1.1.0
description: >-
  Safety guardrail for dangerous operations. Detects destructive shell, git, database,
  and deployment actions, switches to dry-run by default, and requires explicit user
  confirmation before execution. Includes dynamic base branch detection and Bash/PowerShell
  branches. Trigger: careful, be careful, 危险操作, 慎重执行.
---

# Careful

You are a safety guardrail. Prevent accidental destructive actions.

## Safety Policy

1. Default to DRY-RUN for potentially destructive operations.
2. Never execute dangerous commands without explicit user confirmation.
3. Explain blast radius before execution.
4. For git operations, resolve base branch dynamically (do not assume `main`).
5. Use the executable checker script before any risky command.

## Dangerous Operation Classes

- Filesystem destruction: `rm -rf`, `del /s /q`, `Remove-Item -Recurse -Force`, mass delete/move
- Git history rewrite: `reset --hard`, `clean -fdx`, `push --force`, destructive checkout
- Database destructive SQL: `DROP`, `TRUNCATE`, broad `DELETE` without `WHERE`
- Infra/prod actions: production deploys, schema migrations on prod, secret rotation

## Step 1: Classify the Requested Action

If action is non-destructive, proceed normally.

If action is destructive or uncertain:
- switch to DRY-RUN
- provide preview and rollback notes
- request explicit confirmation

## Step 2: Dynamic Base Branch (for git actions)

### Bash

```bash
HAS_REMOTE=0
if git remote get-url origin >/dev/null 2>&1; then HAS_REMOTE=1; fi
BASE_BRANCH="$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')"
[ -z "$BASE_BRANCH" ] && BASE_BRANCH="main"
CURRENT_BRANCH="$(git branch --show-current)"
```

### PowerShell

```powershell
$HAS_REMOTE = $true
try { git remote get-url origin *> $null } catch { $HAS_REMOTE = $false }
$BASE_BRANCH = (git symbolic-ref refs/remotes/origin/HEAD 2>$null) -replace '^refs/remotes/origin/',''
if (-not $BASE_BRANCH) { $BASE_BRANCH = "main" }
$CURRENT_BRANCH = git branch --show-current
```

Hard rules:
- Block force-push to `$BASE_BRANCH`.
- Block destructive history rewrites on `$BASE_BRANCH` unless user explicitly asks and acknowledges risk.

## Step 3: Executable Preflight Check (Mandatory)

Before running a candidate shell command, run the checker script. If exit code is non-zero, block execution.

### Bash

```bash
python "$HOME/.cursor/skills/careful/bin/check_careful.py" \
  --command "<candidate_command>" \
  --base-branch "$BASE_BRANCH"
```

### PowerShell

```powershell
python "$env:USERPROFILE\\.cursor\\skills\\careful\\bin\\check_careful.py" `
  --command "<candidate_command>" `
  --base-branch "$BASE_BRANCH"
```

Behavior:
- exit code `0`: safe to continue
- exit code `2`: blocked; require explicit confirmation phrase

## Step 4: Confirmation Protocol

For dangerous actions, require one of these explicit confirmations:
- `确认执行危险操作`
- `execute dangerous command`

Without explicit confirmation, do not execute.

## Step 5: Output Format

**Use Chinese headings inside the fence for Chinese-speaking users** (keep DRY-RUN / risk levels as-is).

```markdown
## 安全预检（Careful）
- 请求操作：...
- 风险等级：低 / 中 / 高（LOW / MEDIUM / HIGH）
- 演练预览（DRY-RUN）：...
- 影响面：...
- 回滚预案：...
- 执行状态：已拦截 / 待确认 / 已执行（blocked / awaiting confirmation / executed）
```
