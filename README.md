# My Cursor Skills

Personal Cursor IDE skills collection. Portable across machines and accounts.

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

| Skill | Description |
|-------|-------------|
| `deep-analysis` | 5-phase adversarial analysis framework for markets, strategies, architectures |
| `code-simplifier` | Simplify and refine Python code for clarity and maintainability |

## Adding a New Skill

1. Create a folder under `skills/` with a `SKILL.md`
2. Optionally add `examples.md`, `references/`, `scripts/`, `assets/`
3. Commit and push
4. Re-run the install script on each machine

## Uninstall

Delete the corresponding folders from `~/.cursor/skills/` (or `%USERPROFILE%\.cursor\skills\` on Windows).