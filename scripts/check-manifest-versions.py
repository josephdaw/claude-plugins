#!/usr/bin/env python3
"""Fail when the marketplace entry and the plugin manifest disagree on a version."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"


def main() -> int:
    listed = json.loads(MARKETPLACE.read_text())["plugins"]
    problems = []
    for entry in listed:
        manifest = ROOT / entry["source"].lstrip("./") / ".claude-plugin" / "plugin.json"
        own = json.loads(manifest.read_text())["version"]
        if own != entry["version"]:
            problems.append(
                f"{entry['name']}: marketplace.json says {entry['version']}, "
                f"{manifest.relative_to(ROOT)} says {own}"
            )
        else:
            print(f"{entry['name']}: {own}")
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
