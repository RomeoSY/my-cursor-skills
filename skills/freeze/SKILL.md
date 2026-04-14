---
name: freeze
version: 1.1.0
description: >-
  Edit-boundary lock for focused and safe work. Restricts write operations to a single
  allowed path and blocks out-of-scope edits by default. Stores lock state in
  `.cursor/freeze-scope.json`. Includes Bash/PowerShell instructions and dry-run behavior
  for out-of-scope actions. Trigger: freeze, lock scope, 限制改动范围, 只改这个目录.
---

# Freeze

You are a scope guard. Restrict write operations to a single allowed path.

## Safety Policy

1. Once frozen, block all write operations outside the locked scope.
2. Read-only operations outside scope are allowed.
3. If requested action is outside scope, switch to DRY-RUN and explain why blocked.
4. Freeze only changes boundaries; it does not auto-run dangerous commands.

## Lock File

- Path: `.cursor/freeze-scope.json` (workspace-local)
- Schema:

```json
{
  "enabled": true,
  "allowedRoot": "<absolute path>",
  "createdAt": "<ISO timestamp>",
  "note": "<optional context>"
}
```

## Step 1: Resolve and Validate Target Scope

- Accept a user-provided directory/file path as boundary.
- Resolve to an absolute path.
- If path does not exist, stop and ask for correction.

## Step 2: Create/Update Lock

### Bash

```bash
mkdir -p .cursor
python "$HOME/.cursor/skills/freeze/bin/set_freeze_scope.py" \
  --allowed-root "<user_scope_path>" \
  --state-file ".cursor/freeze-scope.json" \
  --note "freeze scope"
```

### PowerShell

```powershell
New-Item -ItemType Directory -Force .cursor | Out-Null
python "$env:USERPROFILE\\.cursor\\skills\\freeze\\bin\\set_freeze_scope.py" `
  --allowed-root "<user_scope_path>" `
  --state-file ".cursor/freeze-scope.json" `
  --note "freeze scope"
```

## Enforcement Rules

- Allowed writes: create/edit/delete files under `allowedRoot`.
- Blocked writes: any path outside `allowedRoot`.
- Blocked commands must return a scope warning plus remediation:
  - narrow task to allowed scope, or
  - run `unfreeze`, or
  - reset freeze with a new scope.

Before any write action (`Edit` / `Write` / file delete), run the scope checker:

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

Behavior:
- exit code `0`: path is allowed
- exit code `2`: blocked, stay DRY-RUN and ask user whether to widen scope

## Git Note

When freeze is active and git commands are requested:
- allow status/diff/log broadly
- block mutating commands that stage/edit files outside `allowedRoot`
- for merge/rebase/cherry-pick, default to DRY-RUN unless user explicitly confirms

For git-related workflows, resolve base branch dynamically:

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

**Use Chinese headings inside the fence for Chinese-speaking users.**

```markdown
## 已启用改动范围冻结（Freeze）
- 允许写入的根路径：...
- 锁文件：.cursor/freeze-scope.json
- 策略：超出范围的写入将被拦截
- 状态：生效中（active）
```
