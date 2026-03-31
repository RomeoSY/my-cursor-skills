#!/usr/bin/env python3
"""Dangerous command checker for the careful skill."""

from __future__ import annotations

import argparse
import json
import re
import sys


def is_safe_rm_exception(command: str) -> bool:
    safe_targets = (
        "node_modules",
        ".next",
        "dist",
        "__pycache__",
        ".cache",
        "build",
        ".turbo",
        "coverage",
    )
    if "rm -rf" not in command and "rm -r" not in command:
        return False
    return any(target in command for target in safe_targets)


def detect_risks(command: str, base_branch: str) -> list[str]:
    lower = command.lower()
    risks: list[str] = []

    patterns = [
        (r"\brm\s+-r[f]?\b", "recursive delete"),
        (r"\bremove-item\b.*\b-recurse\b.*\b-force\b", "recursive delete"),
        (r"\bdel\b.*\s/s\b.*\s/q\b", "recursive delete"),
        (r"\bdrop\s+table\b|\bdrop\s+database\b|\btruncate\b", "destructive sql"),
        (r"\bgit\s+reset\s+--hard\b", "git hard reset"),
        (r"\bgit\s+clean\s+-fdx\b", "git clean destructive"),
        (r"\bkubectl\s+delete\b", "kubernetes delete"),
        (r"\bdocker\s+system\s+prune\b|\bdocker\s+rm\s+-f\b", "docker destructive"),
    ]

    for pattern, label in patterns:
        if re.search(pattern, lower):
            risks.append(label)

    if re.search(r"\bgit\s+push\b.*(--force|-f)\b", lower):
        risks.append("force push")
        if re.search(rf"\bgit\s+push\b.*\b{re.escape(base_branch.lower())}\b", lower):
            risks.append(f"force push to base branch '{base_branch}'")

    if is_safe_rm_exception(lower):
        risks = [r for r in risks if r != "recursive delete"]

    return sorted(set(risks))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--command", required=True, help="Candidate shell command.")
    parser.add_argument("--base-branch", default="main", help="Resolved base branch.")
    args = parser.parse_args()

    risks = detect_risks(args.command, args.base_branch)
    payload = {
        "safe": len(risks) == 0,
        "baseBranch": args.base_branch,
        "command": args.command,
        "risks": risks,
    }
    print(json.dumps(payload, ensure_ascii=True))
    if risks:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
