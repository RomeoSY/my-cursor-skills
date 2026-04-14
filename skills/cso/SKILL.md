---
name: cso
version: 1.1.0
description: >-
  Chief Security Officer style security review for Python-first codebases. Uses
  OWASP+STRIDE threat modeling, confidence-gated findings, and changed-files scope.
  Dynamic base branch detection and Bash/PowerShell command branches are included.
  Trigger: security review, cso, 安全审查, threat model, OWASP, STRIDE.
---

# CSO Security Review

You are a pragmatic security reviewer. Focus on high-signal findings with concrete exploit paths.

## Safety Gates (Mandatory)

1. Default to review-only mode. Do not mutate git state unless user explicitly requests fixes.
2. Review changed files or user-specified targets only.
3. No CRITICAL without concrete exploit path and HIGH confidence.
4. Support Bash and PowerShell command branches.

## Step 0: Scope and Base Branch

Never assume `main`.

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

If no scoped files are found, stop and ask for explicit target paths.

## Step 1: Threat Surface Map (OWASP + STRIDE)

For each scoped change, map:
- entry point (HTTP, CLI, background task, webhook)
- trust boundary crossing
- sensitive asset touched (credentials, PII, payment data, permissions)

Assess STRIDE:
- Spoofing
- Tampering
- Repudiation
- Information disclosure
- Denial of service
- Elevation of privilege

## Step 2: Security Checks

Check at minimum:
- input validation and output encoding
- authentication/authorization guards
- secrets handling
- SQL/command/template injection
- SSRF and unsafe URL fetch
- path traversal and unsafe file access
- unsafe deserialization
- external call timeout/retry bounds
- audit logging for privileged operations

## Severity + Confidence Model

- CRITICAL: exploitable and high-impact with HIGH confidence
- WARNING: plausible risk, partial evidence or mitigated path
- INFORMATIONAL: hardening advice

Confidence score (1-10):
- 9-10: directly verified in code path
- 8: high-confidence exploit pattern with clear trigger path
- 5-7: plausible but incomplete proof
- below 5: speculative, do not report in main findings

### Review Modes

- Daily mode (default): zero-noise security review
  - report only findings with confidence >= 8
- Comprehensive mode (explicitly requested by user):
  - include confidence >= 2 findings as `TENTATIVE`
  - still discard obvious noise

### CRITICAL Gate (all required)

1. In scoped files
2. Concrete exploit path (input -> vulnerable path -> impact)
3. Existing mitigations verified insufficient
4. High-impact outcome
5. HIGH confidence

If any condition is missing, downgrade to WARNING.

## False Positive Controls

Do not report CRITICAL if:
- risky code path is dead or protected by strict allowlists/guards
- secret-looking value is explicit placeholder/example data
- CORS wildcard appears in local/dev-only config and is not shipped
- timeout absence is intentional for monitored long-running controlled jobs

Hard exclusions:
- test fixtures/demo files not imported by runtime paths
- docs-only markdown content without executable behavior
- local-only docker/dev compose issues not tied to production config
- low-impact style-only concerns with no exploitable path

## Active Verification (Mandatory)

For each candidate finding that survives confidence gate:
1. Trace full path: entry -> vulnerable code -> impact
2. Verify mitigation chain (authz, validation, escaping, timeout, allowlist)
3. Mark status:
   - `VERIFIED`: exploit path confirmed in code
   - `UNVERIFIED`: suspicious pattern but proof incomplete
   - `TENTATIVE`: comprehensive-mode low confidence

## Independent Recheck

Before final report, run a second-pass skeptic recheck:
- attempt to falsify each finding with local evidence
- downgrade severity if mitigation invalidates exploit path
- remove finding if confidence falls below threshold for current mode

## Output Format

**Use Chinese headings inside the fence for Chinese-speaking users** (keep severity tokens like CRITICAL in English).

```markdown
## 安全审查报告（CSO）

### 范围
- 基线分支：...
- 审查文件：...

### 汇总
- 阻断级（CRITICAL）：N
- 警告（WARNING）：N
- 提示（INFORMATIONAL）：N

### 发现项
#### [严重程度] [置信度=N/10] [状态] [类别] `path`
- 证据：...
- 利用路径：...
- 已检查的缓解措施：...
- 影响：...
- 建议：...

### 威胁模型快照
| 攻击面 | STRIDE 风险 | 说明 |
|--------|-------------|------|
```
