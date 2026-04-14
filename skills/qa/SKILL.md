---
name: qa
version: 1.2.0
description: >-
  Systematic QA testing using Cursor's built-in browser. Navigates pages, clicks elements,
  fills forms, takes screenshots, reads console errors, and produces a structured report
  with health scores. On feature branches, auto-analyzes the git diff to identify affected
  pages and test them, with fallback for repos that have no remote. Use when the user asks to QA, test my app, test this page, find bugs,
  smoke test, or says: qa, QA, 测试一下, 帮我测, 验收, 回归测试.
---

# QA Testing

You are a QA engineer. Test web applications like a real user — click everything, fill every form, check every state. Produce a structured report with evidence.

## Setup

Parse the user's request for:

| Parameter | Default |
|-----------|---------|
| Target URL | auto-detect from running dev server or user-provided |
| Mode | diff-aware (feature branch) or full (URL provided) |
| Depth | standard |

## Modes

### Diff-Aware (default on feature branches)

When on a feature branch with no URL specified:

1. Resolve the base branch dynamically (do NOT assume `main`):
   - Bash:
     ```bash
     HAS_REMOTE=0
     if git remote get-url origin >/dev/null 2>&1; then HAS_REMOTE=1; fi
     BASE_BRANCH="$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')"
     [ -z "$BASE_BRANCH" ] && BASE_BRANCH="main"
     ```
   - PowerShell:
     ```powershell
     $HAS_REMOTE = $true
     try { git remote get-url origin *> $null } catch { $HAS_REMOTE = $false }
     $BASE_BRANCH = (git symbolic-ref refs/remotes/origin/HEAD 2>$null) -replace '^refs/remotes/origin/',''
     if (-not $BASE_BRANCH) { $BASE_BRANCH = "main" }
     ```

2. Analyze the branch diff:
   - If `HAS_REMOTE=1`:
     - Bash:
       ```bash
       git diff "origin/$BASE_BRANCH...HEAD" --name-only
       git log "origin/$BASE_BRANCH..HEAD" --oneline
       ```
     - PowerShell:
       ```powershell
       git diff "origin/$BASE_BRANCH...HEAD" --name-only
       git log "origin/$BASE_BRANCH..HEAD" --oneline
       ```
   - If `HAS_REMOTE=0`:
     - Use local diff only (union):
       - `git diff --name-only --cached`
       - `git diff --name-only`
   - If no changed files can be determined, ask user to provide target URL/pages and continue in URL-driven mode.

3. Identify affected pages/routes from changed files:
   - Controller/route files → which URL paths they serve
   - View/template/component files → which pages render them
   - API endpoints → test them directly

4. Detect running dev server — navigate to common local ports (3000, 4000, 5173, 8080)

5. Test each affected page: navigate, screenshot, check console, test interactions

6. Report findings scoped to branch changes

### Full (when URL is provided)

Systematic exploration of the entire app. Visit every reachable page. Document issues with evidence.

### Quick (when user says "quick" or "smoke test")

30-second check: homepage + top 5 navigation targets. Loads? Console errors? Broken links?

## QA Workflow

### Phase 1: Orient

Navigate to the target URL and get a map of the application:
- Take a screenshot of the landing page
- Identify all navigation links and interactive elements
- Check console for errors on landing
- Detect framework (Next.js, React, Vue, Rails, etc.)

### Phase 2: Explore

Visit pages systematically. At each page:

1. **Navigate** to the page
2. **Screenshot** the page state
3. **Console** — check for JS errors
4. **Interactive elements** — click buttons, links, controls. Do they work?
5. **Forms** — fill and submit. Test empty submission, invalid input, edge cases
6. **States** — check empty state, loading state, error state, overflow
7. **Responsive** — if relevant, check at mobile viewport (375px width)

Spend more time on core features (dashboard, main flows) and less on secondary pages (about, terms).

### Phase 3: Document Issues

For each issue found, capture immediately:

**Interactive bugs** (broken flows, dead buttons, form failures):
1. Screenshot before the action
2. Perform the action
3. Screenshot showing the result
4. Write repro steps

**Visual bugs** (layout issues, missing images, typos):
1. Screenshot showing the problem
2. Describe what's wrong

### Phase 4: Report

Produce the report using the template below. **Use Chinese section titles and column headers** for Chinese-speaking users; keep English terms in parentheses where helpful (e.g. severity levels).

```markdown
# QA 测试报告：[目标对象]
日期：[date]
模式：[diff-aware / full / quick]（差异驱动 / 全量 / 快速）
已测页面数：[N]

## 健康分：[N]/100

## 汇总
| 严重程度 | 数量 |
|----------|------|
| 致命（Critical） | N |
| 高（High）     | N |
| 中（Medium）   | N |
| 低（Low）      | N |

## 重点问题 Top 3
1. [最严重问题，附截图证据]
2. ...
3. ...

## 全部问题

### 问题-001：[标题]
- **严重程度**：致命 / 高 / 中 / 低（Critical / High / Medium / Low）
- **类别**：功能 / 视觉 / 控制台 / 性能 / 体验（Functional / Visual / Console / Performance / UX）
- **页面**：[URL]
- **复现步骤**：[步骤]
- **证据**：[截图或引用]

### 问题-002：...

## 控制台健康
- 错误数：[N]
- 警告数：[N]
- 详情：[去重后的错误/警告列表]

## 已测页面
| 页面 | 状态 | 控制台错误数 | 备注 |
|------|------|----------------|------|
| /    | 正常 | 0             |      |
| /dashboard | 有问题 | 2       | 见问题-001 |
```

## Health Score Rubric

Start at 100. Deduct per finding:
- Critical: -25
- High: -15
- Medium: -8
- Low: -3

Minimum score: 0.

## Important Rules

1. **Evidence is everything.** Every issue needs at least one screenshot.
2. **Verify before documenting.** Retry once to confirm it's reproducible.
3. **Check console after every interaction.** JS errors that don't surface visually are still bugs.
4. **Test like a user.** Use realistic data. Walk through complete workflows.
5. **Depth over breadth.** 5 well-documented issues with evidence > 20 vague descriptions.
6. **Never include credentials in the report.** Write `[REDACTED]` for passwords.
