---
name: ship
version: 1.2.0
description: >-
  Safe ship workflow with default dry-run mode. Syncs with base branch, runs tests,
  performs a stop-ship quick review, drafts commit and PR content, and only executes
  commit/push/PR when the user explicitly requests live execution. Works with or without
  remote repositories. Use when the user
  says: ship, ship it, 发布, 提交, 推上去, push, 帮我提PR, create PR.
---

# Ship

You are a release engineer. The workflow must be safe by default.

## Execution Mode (Mandatory)

Default to **DRY-RUN**.

- **DRY-RUN (default):** analyze, run checks/tests, and output exact commands + PR draft. Do NOT mutate git state (`commit`, `push`, `pr create`).
- **LIVE:** only when user explicitly asks to execute, with phrases like:
  - "执行 push"
  - "现在提交并推送"
  - "create PR now"
  - "run live ship"

If explicit execution intent is missing, stay in DRY-RUN.

## Base Branch & Shell Compatibility

Do NOT assume `main`. Resolve base branch dynamically.

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

Use `$BASE_BRANCH` in all diff/log/fetch/merge operations.

## Step 1: Pre-flight

```bash
git branch --show-current
```

If current branch equals `$BASE_BRANCH`: abort — "Ship from a feature branch, not the base branch."

```bash
git status
```

Then inspect scope:

- If `HAS_REMOTE=1`:
  ```bash
  git diff origin/$BASE_BRANCH...HEAD --stat
  git log origin/$BASE_BRANCH..HEAD --oneline
  ```
- If `HAS_REMOTE=0`:
  ```bash
  git diff --stat --cached
  git diff --stat
  git log --oneline -20
  ```

Understand what's being shipped. Uncommitted changes are always included.

## Step 2: Sync Strategy

- If `HAS_REMOTE=1`:
  - In **DRY-RUN**: do not merge. Only preview divergence:
    ```bash
    git fetch origin $BASE_BRANCH
    git log --oneline --left-right HEAD...origin/$BASE_BRANCH
    ```
  - In **LIVE**: merge base branch before tests:
    ```bash
    git fetch origin $BASE_BRANCH
    git merge origin/$BASE_BRANCH --no-edit
    ```
    If merge conflicts are complex, stop and show conflicts.
- If `HAS_REMOTE=0`:
  - In **DRY-RUN**: skip fetch/merge and use local history only.
  - In **LIVE**: do not attempt merge; continue with local branch state and clearly note that base sync is skipped due to missing remote.

## Step 3: Run Tests

Detect the project type and run the appropriate test suite (Python first):

| Project Type | Detection | Commands |
|-------------|-----------|----------|
| Python | `pyproject.toml` or `setup.py` or `pytest.ini` | `ruff check . && pytest` |
| Python (strict) | `mypy.ini` or `[tool.mypy]` in pyproject | `ruff check . && mypy . && pytest` |
| npm/pnpm | `package.json` | `npm test` or `pnpm test` |
| Maven | `pom.xml` | `mvn compile test` |
| Gradle | `build.gradle` | `./gradlew build test` |

If any test fails: show failures and **STOP**.

If all pass: note the counts and continue.

## Step 4: Stop-Ship Quick Review

Scan scoped diff for critical issues only:

- If `HAS_REMOTE=1`: `git diff origin/$BASE_BRANCH...HEAD`
- If `HAS_REMOTE=0`: `git diff --cached` and `git diff`

- SQL injection or unsanitized user input
- Hardcoded secrets or credentials
- Missing timeout/retry/error handling on new external calls
- Obvious race conditions or resource leaks

If critical issues found: present each one, ask Fix/Acknowledge/Skip. Apply fixes if requested, then re-run tests.

If no critical issues: continue.

## Step 5: Commit

Analyze the diff and create clean commits:

- If total diff is small (<50 lines, <4 files): single commit is fine
- If larger: split into logical commits (infrastructure first, then features, then tests)

Commit message format:
```
<type>: <concise description>
```
Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`

### DRY-RUN behavior

Do NOT commit. Output exact proposed commands:

```bash
git add -A
git commit -m "<type>: <description>"
```

### LIVE behavior

Execute commit commands.

## Step 6: Push & PR

### DRY-RUN behavior (default)

Do NOT push. Do NOT create PR. Output exact commands only:

```bash
git push -u origin HEAD
gh pr create --title "<title>" --body "<description>"
```

### LIVE behavior (explicit user intent required)

Run:

```bash
git push -u origin HEAD
```

If `gh` is available and user asked for PR creation, run `gh pr create` and return PR URL.

## Step 7: PR Draft Output

Collect automatically (do not ask the user):
- Branch name: `git rev-parse --abbrev-ref HEAD`
- Changed files:
  - If `HAS_REMOTE=1`: `git diff origin/$BASE_BRANCH...HEAD --stat`
  - If `HAS_REMOTE=0`: combine `git diff --stat --cached` and `git diff --stat`
- Commit log:
  - If `HAS_REMOTE=1`: `git log origin/$BASE_BRANCH..HEAD --oneline`
  - If `HAS_REMOTE=0`: `git log --oneline -20`

Infer change type from paths and commit messages: feature, fix, refactor, or docs.

Output (use Chinese section titles below for Chinese-speaking users):

```markdown
# 拉取请求（PR）草稿

## 标题
<type>: <一句话摘要>

## 说明
本 PR <新增/修复/更新> …

- <要点 1>
- <要点 2>
- <要点 3>

## 测试计划
- [x] 自动化测试已通过
- [ ] 已对受影响流程做手工验收（如适用）
```

## Final Output Rules

- In **DRY-RUN**: label output as `DRY-RUN` and list commands not executed.
- In **LIVE**: label as `LIVE EXECUTION` and include execution results.
- Never silently switch from DRY-RUN to LIVE.
- If intent is unclear, stay DRY-RUN.
