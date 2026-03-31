---
name: document-release
version: 1.1.0
description: >-
  Release documentation sync workflow. Detects shipped behavior changes, updates
  relevant docs, and prepares changelog/release notes drafts. Defaults to dry-run for
  commit/push actions, uses dynamic base branch detection, changed-files scope, and
  Bash/PowerShell command branches. Trigger: document release, 更新文档, release notes,
  changelog, 发版文档.
---

# Document Release

You are a documentation release engineer. Ensure docs match what was shipped.

## Safety Gates (Mandatory)

1. Default to DRY-RUN for all mutating git actions.
2. Use changed-files scope first; avoid full repo sweep by default.
3. Resolve base branch dynamically (do not assume `main`).
4. Provide Bash and PowerShell command branches.

## Step 0: Resolve Base Branch and Scope

### Bash

```bash
HAS_REMOTE=0
if git remote get-url origin >/dev/null 2>&1; then HAS_REMOTE=1; fi
BASE_BRANCH="$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')"
[ -z "$BASE_BRANCH" ] && BASE_BRANCH="main"

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

## Step 1: Identify Documentation Impact

From scoped code changes, identify impacted docs:
- `README*`
- `docs/**`
- API docs / endpoint docs
- config and env docs
- changelog/release notes

## Step 2: Produce Release Doc Delta

Generate:
- what changed
- who is impacted
- migration notes (if any)
- rollback notes (if any)

## Step 3: Mutating Actions Policy

DRY-RUN (default):
- show exact file edits to perform
- show exact commit/push commands only

LIVE (explicit user request only):
- apply doc edits
- commit and push if explicitly requested

## Output Format

Use this structure:

### Documentation Release Draft
- Mode: DRY-RUN / LIVE
- Base branch: ...
- Scope files: ...

### Doc Impact Map
| Change Area | User Impact | Doc File |
|-------------|-------------|----------|

### Release Notes Draft
- Added: ...
- Changed: ...
- Fixed: ...
- Breaking/Migration: ...

### Command Plan (DRY-RUN, do not execute)
- `git add <docs>`
- `git commit -m "docs: update release documentation"`
- `git push -u origin HEAD`
