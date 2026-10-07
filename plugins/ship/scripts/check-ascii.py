#!/usr/bin/env python3
"""Check that text is plain ASCII.

Copied into repos by ship:adopt (at .claude/ship/check-ascii.py). Edit the
source in the ship plugin, not the copy.

Usage, one or more modes per run:
  check-ascii.py --body-file PATH         check the whole file
  check-ascii.py --diff BASE               check only added lines in
                                            changed *.md files between
                                            `git merge-base BASE HEAD`
                                            and the working tree
  check-ascii.py --files PATH [PATH ...]   check whole files

Reports each hit as `path:line: U+XXXX <name>`. Exits 1 on any hit, exits
0 and prints nothing (or one "ok" line when run with no hits) when clean.
"""

import argparse
import subprocess
import sys
import unicodedata
from pathlib import Path

Hit = tuple[str, int, str]


def scan_text(label: str, text: str) -> list[Hit]:
    hits: list[Hit] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for ch in line:
            if ord(ch) > 127:
                hits.append((label, line_no, ch))
    return hits


def scan_whole_file(path: str) -> list[Hit]:
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    return scan_text(path, text)


def added_lines_by_file(diff_output: str) -> dict[str, dict[int, str]]:
    """Map changed *.md path to {new line number: added line text}."""
    result: dict[str, dict[int, str]] = {}
    current_file = ""
    new_line_no = 0
    for raw in diff_output.splitlines():
        if raw.startswith("+++ "):
            path = raw[4:]
            current_file = path[2:] if path.startswith("b/") else path
            result.setdefault(current_file, {})
            continue
        if raw.startswith("@@"):
            # @@ -a,b +c,d @@
            plus_part = raw.split("+", 1)[1].split("@@")[0].strip()
            new_line_no = int(plus_part.split(",")[0])
            continue
        if raw.startswith("+++") or raw.startswith("---"):
            continue
        if raw.startswith("+"):
            result.setdefault(current_file, {})[new_line_no] = raw[1:]
            new_line_no += 1
        elif not raw.startswith("-"):
            new_line_no += 1
    return result


def scan_diff(base: str) -> list[Hit]:
    merge_base = subprocess.run(
        ["git", "merge-base", base, "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    diff_output = subprocess.run(
        ["git", "diff", merge_base, "--", "*.md"],
        capture_output=True, text=True, check=True,
    ).stdout
    hits: list[Hit] = []
    for path, lines in added_lines_by_file(diff_output).items():
        for line_no, line in sorted(lines.items()):
            for ch in line:
                if ord(ch) > 127:
                    hits.append((path, line_no, ch))
    return hits


def report(hits: list[Hit]) -> int:
    if not hits:
        print("ok")
        return 0
    for path, line_no, ch in hits:
        name = unicodedata.name(ch, "UNKNOWN")
        print(f"{path}:{line_no}: U+{ord(ch):04X} {name}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--body-file")
    parser.add_argument("--diff")
    parser.add_argument("--files", nargs="+")
    args = parser.parse_args()

    if not (args.body_file or args.diff or args.files):
        parser.error("give at least one of --body-file, --diff, --files")

    hits: list[Hit] = []
    if args.body_file:
        hits.extend(scan_whole_file(args.body_file))
    if args.diff:
        hits.extend(scan_diff(args.diff))
    if args.files:
        for path in args.files:
            hits.extend(scan_whole_file(path))

    return report(hits)


if __name__ == "__main__":
    sys.exit(main())
