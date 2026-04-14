---
name: impl-strategy
version: 1.2.0
description: >-
  Decide how to implement changes before editing code. Determines the compatibility
  boundary: is this a released public API, an unreleased branch-local change, an internal
  helper, or a persisted schema? Prevents unnecessary shims and over-engineering while
  protecting real contracts. Use before editing runtime or API code, when the user asks
  about backward compatibility, migration strategy, or says: 兼容性, 怎么改, 影响范围,
  breaking change, implementation strategy.
---

# Implementation Strategy

Use this skill before editing code when the task changes runtime behavior or anything that might be a compatibility concern. The goal is to keep implementations simple while protecting real contracts.

## Step 1: Identify the Surface

Classify what you are changing into one of these categories:

| Surface | Compatibility Required? | Action |
|---------|------------------------|--------|
| **Released public API** (endpoints, SDK methods, CLI flags documented to users) | YES | Preserve compatibility or provide explicit migration path |
| **Persisted schema** (DB tables, serialized objects, wire protocols, config files) | YES | Treat as compatibility-sensitive |
| **Unreleased branch-local code** (only exists on current branch) | NO | Rewrite directly |
| **On main but after last release tag** (not yet shipped to users) | NO | Rewrite directly |
| **Internal helpers, private methods** | NO | Update directly |
| **Tests, fixtures, examples** | NO | Update directly |

## Step 2: Find the Release Boundary

Use shell-appropriate commands:

### Bash

```bash
if git remote get-url origin >/dev/null 2>&1; then git fetch --tags origin --quiet || true; fi
git tag -l --sort=-v:refname | head -5
```

### PowerShell

```powershell
try { git remote get-url origin *> $null; git fetch --tags origin --quiet } catch { }
git tag -l --sort=-v:refname | Select-Object -First 5
```

The latest release tag is the compatibility boundary. Prefer remote-refreshed tags when possible, and judge breaking-change risk against that boundary rather than unreleased branch churn.

If no tags exist: the project has no released contract yet — everything can be rewritten.

## Step 3: Apply the Default Stance

**Prefer deletion or replacement** over aliases, overloads, shims, feature flags, and dual-write logic — unless the old shape is part of a released contract.

Checklist:
- [ ] Is the old interface released? If NO → delete/replace, no shim
- [ ] Is there a persisted schema involved? If YES → migration needed
- [ ] Is there an external consumer? If YES → deprecation path
- [ ] Is review feedback claiming "breaking change"? Verify against release tag first

Do NOT:
- Preserve a confusing abstraction just because it exists in the current diff
- Add backward-compatibility layers for interfaces only you have used
- Create feature flags for changes that haven't shipped yet

## Step 4: When to Stop and Confirm

Stop and ask the user before proceeding if:
- The change alters behavior shipped in the latest release tag
- The change modifies persisted data, protocol formats, or serialized state
- The user explicitly asked for backward compatibility or migration support

## Output

State the decision briefly (use Chinese for user-facing lines; English terms in parentheses optional):

```
兼容边界（Compatibility boundary）：[最新 release 标签，或「尚无正式发布」]
变更表面（Surface）：[已发布 API / 未发布分支代码 / 内部实现 / persisted schema]
决策（Decision）：[直接重写 / 保留兼容并迁移 / deprecation path]
理由（Rationale）：[一句话]
```

Then proceed with the implementation.

## Python-Specific Surfaces

### Public API
- `__all__` exports in `__init__.py` → public contract
- FastAPI/Flask/Django endpoint paths and response schemas → public if documented
- CLI arguments (`argparse`, `click`, `typer`) → config contract for scripts/tools
- Pydantic model field names used in API responses or serialization → wire protocol
- Function signatures in packages published to PyPI → semver contract

### Persisted Schema
- Alembic / Django migrations → always compatibility-sensitive
- SQLAlchemy model column names and types → persisted
- Pydantic models used with `model_dump()` for storage (Redis, JSON files, message queues) → wire protocol
- `pickle` / `joblib` serialized objects → version-sensitive, avoid across releases

### Config Contract
- `.env` variable names consumed by `pydantic-settings` or `python-decouple`
- `pyproject.toml` `[tool.*]` sections if documented for users
- Config file schemas (YAML/TOML) loaded by the application

### Internal (safe to rewrite)
- Functions/classes not in `__all__` and not imported by other packages
- Private methods (prefixed with `_`)
- Test helpers, fixtures, conftest.py utilities
- Type aliases and internal dataclasses not exposed in API

### Other Languages (reference)

**Node.js / TypeScript**: Exported types from `index.ts` → public API; Prisma/Drizzle migrations → persisted; `.env` vars → config; REST/GraphQL schema → wire protocol.

**Java / Spring Boot**: `@RestController` endpoints → public API; `@Entity` JPA schema → persisted (Flyway/Liquibase); `application.yml` keys → config; Jackson `@JsonProperty` → wire protocol.
