#!/usr/bin/env python3
"""Set freeze scope state file."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
from datetime import datetime, timezone


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allowed-root", required=True)
    parser.add_argument("--state-file", default=".cursor/freeze-scope.json")
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    root = pathlib.Path(args.allowed_root).expanduser().resolve()
    if not root.exists():
        print(json.dumps({"ok": False, "error": "allowed-root not found", "path": str(root)}))
        return 2

    state_path = pathlib.Path(args.state_file).expanduser().resolve()
    state_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "enabled": True,
        "allowedRoot": str(root),
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "note": args.note,
    }
    state_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "stateFile": str(state_path), "allowedRoot": str(root)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
