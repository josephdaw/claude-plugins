#!/usr/bin/env python3
"""Enforce one version convention: plugin.json only, never marketplace.json."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"


def main() -> int:
    listed = json.loads(MARKETPLACE.read_text())["plugins"]
    problems = []
    for entry in listed:
        if "version" in entry:
            problems.append(
                f"{entry['name']}: marketplace.json sets version, but the "
                "version lives in plugin.json only"
            )
            continue
        source = entry["source"].removeprefix("./")
        manifest = ROOT / source / ".claude-plugin" / "plugin.json"
        data = json.loads(manifest.read_text())
        if "version" not in data:
            problems.append(f"{entry['name']}: {manifest.relative_to(ROOT)} has no version")
            continue
        print(f"{entry['name']}: {data['version']}")
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
