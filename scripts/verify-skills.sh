#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 - <<'PYEOF'
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(".")
SKILLS_DIR = ROOT / "skills"
LEGACY_DIR = ROOT / "legacy"
RESOLVER = SKILLS_DIR / "RESOLVER.md"


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def parse_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text().splitlines()
    if not lines or lines[0] != "---":
        fail(f"INVALID FRONTMATTER: {path} must start with ---")

    try:
        end = lines.index("---", 1)
    except ValueError:
        fail(f"INVALID FRONTMATTER: {path} missing closing ---")

    fields: dict[str, str] = {}
    frontmatter = lines[1:end]
    i = 0
    while i < len(frontmatter):
        line = frontmatter[i]
        if not line or line.startswith(" "):
            i += 1
            continue
        key, sep, raw = line.partition(":")
        if sep != ":":
            i += 1
            continue
        value = raw.strip()
        if value in {"|", "|-", "|+", ">", ">-", ">+"}:
            block: list[str] = []
            i += 1
            while i < len(frontmatter):
                child = frontmatter[i]
                if child and not child.startswith(" "):
                    break
                block.append(child.strip())
                i += 1
            fields[key] = "\n".join(part for part in block if part).strip()
            continue
        fields[key] = value.strip().strip('"').strip("'")
        i += 1

    for field in ("name", "description"):
        if not fields.get(field):
            fail(f"MISSING {field}: {path}")

    return fields


def active_skill_files() -> list[Path]:
    files = []
    for child in sorted(SKILLS_DIR.iterdir()):
        if child.name.startswith(".") or child.name == "legacy":
            continue
        skill_file = child / "SKILL.md"
        if skill_file.exists():
            files.append(skill_file)
    return files


skill_files = active_skill_files()
if not skill_files:
    fail("NO ACTIVE SKILLS FOUND")

skill_names: set[str] = set()
for path in skill_files:
    name = path.parent.name
    fields = parse_frontmatter(path)
    if fields["name"] != name:
        fail(f"NAME MISMATCH: {path} frontmatter name={fields['name']} dir={name}")
    if name in skill_names:
        fail(f"DUPLICATE SKILL: {name}")
    skill_names.add(name)
    if path.parent.is_symlink() and not path.parent.exists():
        fail(f"BROKEN SYMLINK: {path.parent}")
    print(f"ok: skill {name}")

if (SKILLS_DIR / "brainstorming").exists():
    fail("LEGACY MOVE INCOMPLETE: skills/brainstorming still exists")
if (SKILLS_DIR / "systematic-debugging").exists():
    fail("LEGACY MOVE INCOMPLETE: skills/systematic-debugging still exists")
for legacy in ("brainstorming", "systematic-debugging"):
    if not (LEGACY_DIR / legacy / "SKILL.md").exists():
        fail(f"LEGACY SKILL MISSING: legacy/{legacy}/SKILL.md")
print("ok: legacy parking")

if not RESOLVER.exists():
    fail("MISSING RESOLVER: skills/RESOLVER.md")
resolver_text = RESOLVER.read_text()
for name in sorted(skill_names):
    token = f"skills/{name}/SKILL.md"
    if token not in resolver_text:
        fail(f"RESOLVER GAP: {token}")
    print(f"ok: resolver entry {name}")

referenced = set(re.findall(r"skills/([a-z][a-z0-9_-]*)/SKILL\.md", resolver_text))
stale = sorted(referenced - skill_names)
if stale:
    fail("RESOLVER REFERENCES MISSING ACTIVE SKILL: " + ", ".join(stale))
print("ok: resolver active references")

ref_pattern = re.compile(r"(?<![/.])\b(?:references|agents|scripts)/[\w/.-]+\b")
for path in skill_files:
    text = path.read_text()
    for ref in sorted(set(ref_pattern.findall(text))):
        expected = path.parent / ref
        if not expected.exists():
            fail(f"BROKEN REFERENCE: {path} references {ref}")
        print(f"ok: reference {path.parent.name}/{ref}")

md_files: list[Path] = [RESOLVER]
for path in skill_files:
    md_files.append(path)
    for subdir in ("references", "agents"):
        root = path.parent / subdir
        if root.is_dir():
            md_files.extend(sorted(root.rglob("*.md")))

link_re = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
url_prefixes = ("http://", "https://", "mailto:", "ftp://", "tel:", "data:")
for path in md_files:
    in_code = False
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        for match in link_re.finditer(line):
            raw = match.group(1).strip()
            if not raw or raw.startswith(("#", "/")):
                continue
            if raw.startswith(url_prefixes) or "://" in raw:
                continue
            target = raw.split("#", 1)[0].split("?", 1)[0]
            if target and not (path.parent / target).resolve().exists():
                fail(f"BROKEN MARKDOWN LINK: {path}:{lineno} -> {raw}")
    print(f"ok: markdown links {path}")

sep_re = re.compile(r"^[\s|:\-]+$")


def pipe_count(value: str) -> int:
    count = 0
    in_tick = False
    i = 0
    while i < len(value):
        if value[i] == "\\" and i + 1 < len(value):
            i += 2
            continue
        if value[i] == "`":
            in_tick = not in_tick
        elif value[i] == "|" and not in_tick:
            count += 1
        i += 1
    return count


for path in md_files:
    in_fence = False
    sep_pipes: int | None = None
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            sep_pipes = None
            continue
        if in_fence:
            sep_pipes = None
            continue
        if sep_re.match(stripped) and "---" in stripped and "|" in stripped:
            sep_pipes = pipe_count(stripped)
            continue
        if sep_pipes is not None and stripped.startswith("|"):
            if pipe_count(stripped) > sep_pipes:
                fail(f"UNESCAPED PIPE IN TABLE: {path}:{lineno}")
            continue
        sep_pipes = None
    print(f"ok: table pipes {path}")

print(f"verified {len(skill_files)} active skills")
PYEOF
