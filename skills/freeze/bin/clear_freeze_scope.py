#!/usr/bin/env python3
"""Clear freeze scope state file."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-file", default=".cursor/freeze-scope.json")
    args = parser.parse_args()

    state_path = pathlib.Path(args.state_file).expanduser().resolve()
    if not state_path.exists():
        print(json.dumps({"ok": True, "removed": False, "reason": "state file not found"}))
        return 0

    previous = ""
    try:
        previous = json.loads(state_path.read_text(encoding="utf-8")).get("allowedRoot", "")
    except Exception:  # noqa: BLE001
        previous = ""
    state_path.unlink(missing_ok=True)
    print(json.dumps({"ok": True, "removed": True, "previousAllowedRoot": previous}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
