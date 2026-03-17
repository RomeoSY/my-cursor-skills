#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SOURCE="$SCRIPT_DIR/skills"
SKILLS_TARGET="$HOME/.cursor/skills"

mkdir -p "$SKILLS_TARGET"

installed=()
for skill_dir in "$SKILLS_SOURCE"/*/; do
    [ -d "$skill_dir" ] || continue
    skill_name="$(basename "$skill_dir")"
    dest="$SKILLS_TARGET/$skill_name"
    rm -rf "$dest"
    cp -r "$skill_dir" "$dest"
    installed+=("$skill_name")
done

echo ""
echo "Installed ${#installed[@]} skill(s) to $SKILLS_TARGET"
for s in "${installed[@]}"; do
    echo "  - $s"
done
echo ""
echo "Restart Cursor to activate."