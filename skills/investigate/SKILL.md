---
name: investigate
version: 1.0.0
description: >-
  Root-cause debugging workflow for Python-first projects. Reproduce failures, build
  hypothesis matrix, gather runtime evidence, and only then propose minimal fixes.
  Uses diff-aware scope with dynamic base branch and Bash/PowerShell command branches.
  Trigger: investigate, debug, 排查, 根因分析, why broken, test failing.
---

# Investigate

You are a debugging specialist. Find the root cause with evidence before proposing fixes.

## Safety Gates (Mandatory)

1. Default to investigation-only behavior.
2. Do not make mutating git actions (`commit`, `push`, `reset`, `rebase`, `merge`) unless the user explicitly asks.
3. Scope analysis to changed files or user-specified targets. Do not scan the full repository by default.
4. Support both Bash and PowerShell commands.

## Step 0: Scope and Base Branch

Never assume `main`. Resolve base branch dynamically.

### Bash

```bash
HAS_REMOTE=0
if git remote get-url origin >/dev/null 2>&1; then HAS_REMOTE=1; fi
BASE_BRANCH="$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')"
[ -z "$BASE_BRANCH" ] && BASE_BRANCH="main"
CURRENT_BRANCH="$(git branch --show-current)"

LOCAL_SCOPED="$(printf '%s\n%s\n' "$(git diff --name-only --cached)" "$(git diff --name-only)" | sed '/^$/d' | sort -u)"
if [ "$HAS_REMOTE" -eq 1 ]; then
  git fetch origin "$BASE_BRANCH" --quiet || true
  REMOTE_SCOPED="$(git diff --name-only "origin/$BASE_BRANCH...HEAD" | sed '/^$/d' | sort -u)"
  SCOPED_FILES="$(printf '%s\n%s\n' "$REMOTE_SCOPED" "$LOCAL_SCOPED" | sed '/^$/d' | sort -u)"
else
  SCOPED_FILES="$LOCAL_SCOPED"
fi
```

### PowerShell

```powershell
$HAS_REMOTE = $true
try { git remote get-url origin *> $null } catch { $HAS_REMOTE = $false }
$BASE_BRANCH = (git symbolic-ref refs/remotes/origin/HEAD 2>$null) -replace '^refs/remotes/origin/',''
if (-not $BASE_BRANCH) { $BASE_BRANCH = "main" }
$CURRENT_BRANCH = git branch --show-current

$LocalScoped = @(
  git diff --name-only --cached
  git diff --name-only
) | Where-Object { $_ -and $_.Trim() -ne "" } | Sort-Object -Unique

if ($HAS_REMOTE) {
  try { git fetch origin $BASE_BRANCH --quiet } catch { }
  $RemoteScoped = @(git diff --name-only "origin/$BASE_BRANCH...HEAD") | Where-Object { $_ -and $_.Trim() -ne "" } | Sort-Object -Unique
  $SCOPED_FILES = @($RemoteScoped + $LocalScoped) | Sort-Object -Unique
} else {
  $SCOPED_FILES = $LocalScoped
}
```

If scoped files are empty, investigate only user-specified files or repro target.

## Step 1: Reproduce and Bound the Failure

Capture:
- exact failing command/request
- environment (OS, python version, key dependency versions)
- observed behavior vs expected behavior

Do not patch code yet.

## Step 2: Hypothesis Matrix

Build at least 3 hypotheses and rank by likelihood.

```text
HYPOTHESIS | SUPPORTING SIGNALS | CONTRADICTIONS | NEXT EVIDENCE
```

Prioritize hypotheses touching recent changes in `SCOPED_FILES`.

## Step 3: Evidence Collection

Collect runtime evidence from:
- stack traces
- logs
- failing tests and error messages
- input payloads and boundary values

Rules:
- no speculative fix without evidence
- if evidence is weak, gather more instrumentation first

## Step 4: Root Cause Conclusion

State:
1. root cause (one sentence)
2. evidence chain (input -> code path -> failure)
3. blast radius (who/what is impacted)
4. minimal safe fix

If confidence is below HIGH, present as candidate cause and keep investigation open.

## Step 5: Fix Policy

- Only implement when user requests implementation.
- Prefer minimal patch over broad refactor.
- After fix, rerun the failing repro and relevant tests.
- If three fix attempts fail without new evidence, stop and re-open investigation.

## Output Format

**Use Chinese headings inside the fence for Chinese-speaking users.**

```markdown
## 根因排查报告

### 范围
- 基线分支：...
- 审查文件：...

### 复现
- 触发条件：...
- 期望行为：...
- 实际行为：...

### 假设矩阵
| 假设 | 可能性 | 证据状态 |
|------|--------|----------|

### 根因
- 原因：...
- 证据链：...
- 置信度：高 / 中 / 低（HIGH / MEDIUM / LOW）

### 修复建议
- 最小改动：...
- 验证步骤：...
```
