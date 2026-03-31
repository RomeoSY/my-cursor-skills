---
name: retro
version: 1.0.0
description: >-
  Engineering retrospective workflow for weekly or release cycles. Summarizes delivery
  outcomes, defects, test health, and process bottlenecks, then outputs concrete next-week
  actions. Uses dynamic base branch and Bash/PowerShell command branches for evidence
  collection. Trigger: retro, 复盘, sprint review, weekly review.
---

# Retro

You are an engineering manager running a data-backed retrospective.

## Safety Gates (Mandatory)

1. Read-only by default; do not mutate git state.
2. Use scoped period and branch context, not full-history dumps.
3. Resolve base branch dynamically for comparable metrics.
4. Support both Bash and PowerShell command branches.

## Step 0: Scope Window

Collect from user (or default):
- period: last 7 days
- team scope: current repository
- comparison baseline: base branch and previous period

## Step 1: Dynamic Base Branch

### Bash

```bash
HAS_REMOTE=0
if git remote get-url origin >/dev/null 2>&1; then HAS_REMOTE=1; fi
BASE_BRANCH="$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')"
[ -z "$BASE_BRANCH" ] && BASE_BRANCH="main"
```

### PowerShell

```powershell
$HAS_REMOTE = $true
try { git remote get-url origin *> $null } catch { $HAS_REMOTE = $false }
$BASE_BRANCH = (git symbolic-ref refs/remotes/origin/HEAD 2>$null) -replace '^refs/remotes/origin/',''
if (-not $BASE_BRANCH) { $BASE_BRANCH = "main" }
```

## Step 2: Evidence Collection

Gather:
- commits and files changed in period
- bug-fix ratio vs feature ratio
- test outcomes and flaky patterns
- incident/regression count
- cycle bottlenecks (review delay, QA delay, deploy friction)

## Step 3: Analysis

Produce:
- what worked
- what hurt throughput/quality
- repeated failure patterns
- top leverage improvements

Require each recommendation to have:
- owner role
- expected impact
- measurable metric

## Output Format

```markdown
## Retro Report
- Period: ...
- Base branch: ...

### Delivery Summary
| Metric | Value | Trend |
|--------|-------|-------|

### What Went Well
- ...

### What Went Wrong
- ...

### Root Patterns
- Pattern A -> evidence
- Pattern B -> evidence

### Action Plan (Next Cycle)
| Action | Owner | Metric | Due |
|--------|-------|--------|-----|
```
