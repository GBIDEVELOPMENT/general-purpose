#!/usr/bin/env python3
"""Dependency-free structure/reference checker. Does not fetch URLs or execute Android code."""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
skill = root / "SKILL.md"
errors = []
try:
    body = skill.read_text(encoding="utf-8")
except OSError as exc:
    sys.exit(f"FAIL: missing SKILL.md: {exc}")
if not body.startswith("---\n") or "\n---\n" not in body[4:]:
    errors.append("SKILL.md needs YAML frontmatter")
else:
    header = body.split("---", 2)[1]
    match = re.search(r"(?m)^name:\s*([^\s]+)\s*$", header)
    if not match or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", match.group(1)) or len(match.group(1)) > 64:
        errors.append("invalid skill name")
    desc = re.search(r"(?m)^description:\s*(.*)$", header)
    if not desc or not desc.group(1).strip() or len(desc.group(1)) > 1024:
        errors.append("invalid description")
if len(body.splitlines()) > 500:
    errors.append("SKILL.md exceeds 500 lines")
for path in root.rglob("*.md"):
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        errors.append(f"empty file: {path}")
    for link in re.findall(r"\]\(([^)]+)\)", text):
        if link.startswith(("https://", "http://", "#", "mailto:")):
            continue
        target = (path.parent / link.split("#", 1)[0]).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError:
            errors.append(f"external local link: {path}: {link}")
            continue
        if not target.exists():
            errors.append(f"missing local link: {path}: {link}")
case = (root / "references" / "historical-casebook.md").read_text(encoding="utf-8")
ids = re.findall(r"\| (?:CH|GL|EX)-\d\d \|", case)
if len(ids) < 12 or len(set(ids)) != len(ids):
    errors.append(f"casebook missing/duplicate cases: {len(ids)}")
if errors:
    for err in errors:
        print("FAIL:", err, file=sys.stderr)
    sys.exit(1)
print(f"PASS: Android skill structure, {len(ids)} casebook entries, internal links, frontmatter")
