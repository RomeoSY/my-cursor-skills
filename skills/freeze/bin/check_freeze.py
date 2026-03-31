#!/usr/bin/env python3
"""Check whether a path is inside freeze scope."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys


def normalize(path_value: str) -> str:
    resolved = pathlib.Path(path_value).expanduser().resolve()
    text = str(resolved)
    if not text.endswith(("/", "\\")):
        text = text + os.sep
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--state-file", default=".cursor/freeze-scope.json")
    args = parser.parse_args()

    state_path = pathlib.Path(args.state_file).expanduser().resolve()
    if not state_path.exists():
        print(json.dumps({"ok": True, "reason": "no freeze state"}))
        return 0

    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": f"invalid freeze state: {exc}"}))
        return 2

    if not state.get("enabled", False):
        print(json.dumps({"ok": True, "reason": "freeze disabled"}))
        return 0

    allowed_root = state.get("allowedRoot", "")
    if not allowed_root:
        print(json.dumps({"ok": False, "error": "missing allowedRoot"}))
        return 2

    allowed_norm = normalize(allowed_root)
    target_norm = normalize(args.target)
    allowed = target_norm.startswith(allowed_norm)
    payload = {
        "ok": allowed,
        "allowedRoot": allowed_root,
        "target": str(pathlib.Path(args.target).expanduser().resolve()),
    }
    print(json.dumps(payload, ensure_ascii=True))
    return 0 if allowed else 2


if __name__ == "__main__":
    sys.exit(main())
