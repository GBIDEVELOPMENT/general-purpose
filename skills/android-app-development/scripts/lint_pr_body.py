#!/usr/bin/env python3
"""Check a local PR description for a known GitHub auto-closure pitfall."""
import argparse
from pathlib import Path
import re
import sys

PATTERN = re.compile(
    r"(?i)\\b(?:do\\s+not|does\\s+not|don't|doesn't|never|won't|"
    r"will\\s+not|should\\s+not|must\\s+not)\\s+"
    r"(?:close|closes|fix|fixes|resolve|resolves)\\s+"
    r"(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)?#([0-9]+)\\b"
)

def findings(body):
    return [(int(m.group(1)), body.count("\\n", 0, m.start()) + 1)
            for m in PATTERN.finditer(body)]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("body", type=Path)
    args = p.parse_args()
    for issue, line in findings(args.body.read_text(encoding="utf-8")):
        print(f"WARNING line {line}: a negated closing keyword may close issue #{issue}.")
    return 1 if findings(args.body.read_text(encoding="utf-8")) else 0

if __name__ == "__main__":
    sys.exit(main())
