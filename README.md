# My Cursor Skills

Personal Cursor IDE skills collection, portable across machines and accounts.

## Quick Install

### Windows (PowerShell)

```powershell
git clone https://github.com/RomeoSY/my-cursor-skills.git "$env:TEMP\my-cursor-skills"
& "$env:TEMP\my-cursor-skills\install.ps1"
```

### Mac / Linux (Bash)

```bash
git clone https://github.com/RomeoSY/my-cursor-skills.git /tmp/my-cursor-skills
bash /tmp/my-cursor-skills/install.sh
```

## Skills

| Skill | Version | Purpose |
|-------|---------|---------|
| `plan-review` | `1.2.0` | Review plans before coding, challenge scope, map risks and failure modes |
| `code-review` | `1.2.1` | Pre-merge risk review focused on production-impact issues |
| `qa` | `1.2.0` | Browser-based QA workflow with evidence-driven reporting |
| `ship` | `1.2.0` | Safe ship flow with default dry-run and optional live execution |
| `impl-strategy` | `1.2.0` | Decide compatibility boundary before implementation |
| `deep-analysis` | `1.0.0` | 5-phase adversarial deep analysis framework |
| `code-simplifier` | `1.1.0` | Simplify/refactor Python code while preserving behavior |

## Add a New Skill

1. Create a folder under `skills/` with `SKILL.md`
2. Optionally add `examples.md`, `references/`, `scripts/`, `assets/`
3. Commit and push
4. Re-run install script on each machine

## Uninstall

Delete corresponding folders under:
- Windows: `%USERPROFILE%\.cursor\skills\`
- Mac/Linux: `~/.cursor/skills/`