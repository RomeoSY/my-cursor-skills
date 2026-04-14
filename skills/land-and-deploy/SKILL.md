---
name: land-and-deploy
version: 1.1.0
description: >-
  Merge-and-deploy workflow after review approval. Verifies branch state, tests,
  CI/deploy readiness, and post-deploy health checks. Defaults to dry-run and only
  executes merge/deploy when the user explicitly requests live execution. Uses dynamic
  base branch and Bash/PowerShell command branches. Trigger: land and deploy, 合并发布,
  上线, merge and deploy, 发布到生产.
---

# Land and Deploy

You are a release operator. Land approved changes and verify production safely.

## Safety Gates (Mandatory)

1. Default mode is DRY-RUN.
2. Do not execute merge/deploy without explicit live intent.
3. Never assume base branch is `main`; resolve dynamically.
4. Validate state using changed-file scope and current branch context.

## Execution Mode

- DRY-RUN (default): analyze and output exact commands, no merge/deploy side effects.
- LIVE (explicit): user says phrases like:
  - `执行发布`
  - `merge and deploy now`
  - `run live land-and-deploy`

## Step 0: Resolve Base Branch and Context

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

## Step 1: Pre-Flight

- Ensure current branch is not base branch.
- Check working tree state.
- Check divergence against base:
  - with remote: `git fetch origin $BASE_BRANCH` then inspect `HEAD...origin/$BASE_BRANCH`
  - no remote: use local log/diff only and clearly report reduced certainty

## Step 2: Quality Gate

Run project checks (Python-first):
- `ruff check .`
- `mypy .` when configured
- `pytest`

If any check fails, stop.

## Step 3: Landing Plan

DRY-RUN:
- output exact merge commands and conflict-risk notes
- output deploy command template

LIVE:
- execute merge strategy requested by user (`merge` or `squash`)
- stop on conflicts and report

## Step 4: CI Gate (Mandatory)

Require passing CI checks before deploy.

If `HAS_REMOTE=1` and `gh` is available:

### Bash

```bash
PR_NUMBER="$(gh pr view --json number --jq '.number' 2>/dev/null || true)"
if [ -z "$PR_NUMBER" ]; then
  echo "No PR found for current branch. Stop and request explicit PR reference."
else
  gh pr checks "$PR_NUMBER" --watch
fi
```

### PowerShell

```powershell
$PR_NUMBER = gh pr view --json number --jq ".number" 2>$null
if (-not $PR_NUMBER) {
  Write-Host "No PR found for current branch. Stop and request explicit PR reference."
} else {
  gh pr checks $PR_NUMBER --watch
}
```

Rules:
- DRY-RUN: print these commands but do not execute merge/deploy.
- LIVE: if checks fail or cannot be verified, stop deployment.
- If `gh` is unavailable, require user-provided CI evidence before LIVE deploy.

## Step 5: Deploy Plan

Require deploy target info:
- environment (`staging` / `prod`)
- deploy command or platform (e.g., `kubectl`, `vercel`, `fly`, `railway`)
- health URL(s)

DRY-RUN:
- print exact deploy and verification commands only

LIVE:
- run deploy command
- perform health checks and smoke checks

## Step 6: Post-Deploy Verification

Verify:
- health endpoint status
- error logs/alerts (if available)
- key user path smoke test

If verification fails, recommend rollback (dry-run by default unless user explicitly requests execution).

## Output Format

**Use Chinese headings inside the fence for Chinese-speaking users.**

```markdown
## 合并与发布报告
- 模式：演练（DRY-RUN）/ 实际执行（LIVE）
- 基线分支：...
- 当前分支：...

### 起飞前检查
- 分支状态：...
- 检查项：通过 / 失败（pass / fail）

### 合并落地
- 策略：merge / squash
- 状态：...

### 部署
- 目标环境：...
- 命令：...
- 状态：...

### 验证
- 健康检查：...
- 烟测：...
- 回滚建议：...
```
