---
name: unfreeze
version: 1.1.0
description: >-
  Remove the workspace edit-boundary lock created by `freeze`. Clears
  `.cursor/freeze-scope.json` and restores normal write scope. Uses safe confirmation
  behavior and cross-platform Bash/PowerShell command branches. Trigger: unfreeze,
  unlock scope, 解除限制, 取消冻结.
---

# Unfreeze

You are a scope unlock tool. Remove active freeze boundaries safely.

## Safety Policy

1. Show current lock state before deleting it.
2. If no lock exists, report "already unfrozen" and stop.
3. Do not run unrelated mutating actions.

## Step 1: Read Current Lock

- Check `.cursor/freeze-scope.json`.
- If found, report `allowedRoot` and `createdAt`.

## Step 2: Remove Lock

### Bash

```bash
python "$HOME/.cursor/skills/freeze/bin/clear_freeze_scope.py" \
  --state-file ".cursor/freeze-scope.json"
```

### PowerShell

```powershell
python "$env:USERPROFILE\\.cursor\\skills\\freeze\\bin\\clear_freeze_scope.py" `
  --state-file ".cursor/freeze-scope.json"
```

## Step 3: Confirm Status

Report final state:
- `active` -> `inactive`
- write scope restored to normal workspace behavior

## Git Note (when follow-up git actions are requested)

Resolve base branch dynamically before any mutating git operation:

### Bash

```bash
BASE_BRANCH="$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')"
[ -z "$BASE_BRANCH" ] && BASE_BRANCH="main"
```

### PowerShell

```powershell
$BASE_BRANCH = (git symbolic-ref refs/remotes/origin/HEAD 2>$null) -replace '^refs/remotes/origin/',''
if (-not $BASE_BRANCH) { $BASE_BRANCH = "main" }
```

## Output Format

```markdown
## Unfreeze Result
- Previous lock: present / absent
- Removed: yes / no
- Current status: inactive
```
