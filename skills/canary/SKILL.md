---
name: canary
version: 1.1.0
description: >-
  Post-deploy canary monitoring loop. Watches for runtime errors, latency regressions,
  and key user-flow failures over a short observation window. Defaults to read-only
  monitoring and dry-run rollback recommendations unless explicit execution is requested.
  Includes Bash/PowerShell command branches and scoped verification targets.
  Trigger: canary, 发布后观察, 上线监控, post deploy monitor.
---

# Canary

You are an SRE-style canary monitor. Validate release health with evidence.

## Safety Gates (Mandatory)

1. Default to read-only monitoring mode.
2. Rollback or config changes are DRY-RUN unless user explicitly asks to execute.
3. Monitor only requested services/endpoints (or changed-feature paths) by default.
4. Provide Bash and PowerShell command branches for checks.

## Step 0: Monitoring Setup

Collect:
- target environment
- service names
- health/check endpoints
- key user paths to validate
- observation window (default 15 minutes)

If monitoring is tied to a release branch, resolve base branch dynamically for change-aware checks:

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

## Step 1: Baseline Snapshot

Capture initial state:
- response status/latency for health endpoints
- recent error logs
- key business action success rate (if available)

Persist evidence under an artifact directory:
- default: `.cursor/canary/<timestamp>/`
- store raw check outputs and summarized metrics

If browser automation is available, capture baseline screenshots for key user paths.

### Bash examples

```bash
# health check
curl -fsS "$HEALTH_URL"

# latency sample
curl -o /dev/null -s -w "%{http_code} %{time_total}\n" "$HEALTH_URL"
```

### PowerShell examples

```powershell
# health check
Invoke-WebRequest -UseBasicParsing $env:HEALTH_URL | Select-Object StatusCode

# latency sample
Measure-Command { Invoke-WebRequest -UseBasicParsing $env:HEALTH_URL *> $null }
```

## Step 2: Canary Loop

Run periodic checks (e.g., every 60-120s):
- endpoint status and latency
- unique error signatures
- key flow smoke tests

Append samples to artifacts (CSV/JSON) so verdict is auditable.

Track trend, not just single-point spikes.

## Step 3: Alert and Thresholds

Trigger canary warning if one of these persists:
- non-2xx health failures
- significant latency regression vs baseline
- repeated new error signatures
- smoke path failure

Suggested default threshold:
- latency regression >= 30% sustained across 3 samples
- health non-2xx on 2 consecutive checks

## Step 4: Response

Default:
- recommend rollback or mitigation in DRY-RUN mode
- include exact rollback commands but do not execute

LIVE only if user explicitly requests:
- run rollback command or mitigation steps

## Step 5: Evidence Bundle

Include in report:
- artifact directory path
- baseline samples count
- anomaly samples count
- screenshot references (if captured)

## Output Format

**Use Chinese headings inside the fence for Chinese-speaking users.**

```markdown
## 金丝雀观测报告
- 模式：仅监控 / 回滚已执行（monitor-only / rollback-live）
- 观测窗口：...
- 观测目标：...

### 基线
- 健康检查：...
- 时延：...
- 错误签名：...

### 观测记录
| 时间 | 健康 | 时延 | 错误 | 烟测路径 |
|------|------|------|------|----------|

### 结论
- 状态：健康 / 降级 / 建议回滚（healthy / degraded / rollback-recommended）
- 依据：...
- 下一步：...

### 产物
- 路径：...
- 文件：...
```
