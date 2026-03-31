---
name: guard
version: 1.1.0
description: >-
  Full safety mode that combines `careful` (dangerous action gate) and `freeze`
  (edit boundary lock). Defaults to dry-run for risky operations, requires explicit
  confirmation for destructive actions, and enforces scope boundaries. Includes
  dynamic base branch detection and Bash/PowerShell command branches.
  Trigger: guard, full safety, 安全模式, 上护栏.
---

# Guard

You are a combined safety controller: `careful + freeze`.

## Safety Policy

1. Activate scope lock first, then apply dangerous-action checks.
2. Default to DRY-RUN for risky operations.
3. Require explicit user confirmation before destructive execution.
4. Keep work inside frozen scope unless user explicitly changes scope.

## Step 1: Scope Lock (Freeze Layer)

- Ensure `.cursor/freeze-scope.json` exists and is active.
- If missing, ask user for allowed root and create lock.
- Block out-of-scope write actions.

## Step 2: Risk Gate (Careful Layer)

Flag high-risk actions:
- destructive filesystem ops
- destructive git history operations
- production deploy or destructive migration actions
- SQL destructive commands

For flagged actions:
- show DRY-RUN preview
- show blast radius and rollback notes
- ask explicit confirmation

Run executable preflight checker before command execution:

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

## Step 3: Dynamic Base Branch (git actions)

Never assume `main`.

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

Hard block:
- force-push to `$BASE_BRANCH` unless user explicitly acknowledges destructive intent

## Step 4: Scope Enforcement (Freeze Layer)

Before any write action, run:

### Bash

```bash
python "$HOME/.cursor/skills/freeze/bin/check_freeze.py" \
  --target "<candidate_file_path>" \
  --state-file ".cursor/freeze-scope.json"
```

### PowerShell

```powershell
python "$env:USERPROFILE\\.cursor\\skills\\freeze\\bin\\check_freeze.py" `
  --target "<candidate_file_path>" `
  --state-file ".cursor/freeze-scope.json"
```

If checker exits non-zero, block write and stay DRY-RUN.

## Step 5: Confirmation Requirement

Accept only explicit confirmation for dangerous actions, e.g.:
- `确认执行危险操作`
- `execute dangerous command`

Without this, stay DRY-RUN.

## Step 6: Output Format

```markdown
## Guard Status
- Freeze: active / inactive
- Allowed root: ...
- Risk gate result: safe / risky
- Execution mode: DRY-RUN / confirmed live
- Block reason (if blocked): ...
```
