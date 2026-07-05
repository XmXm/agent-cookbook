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


def collect_skills() -> tuple[list[Path], set[str]]:
    files: list[Path] = []
    unmounted: set[str] = set()
    for child in sorted(SKILLS_DIR.iterdir()):
        if child.name.startswith(".") or child.name == "legacy":
            continue
        skill_file = child / "SKILL.md"
        if skill_file.exists():
            files.append(skill_file)
            continue
        if child.is_symlink():
            # mt-skills is access-gated (company git): a dangling link into it
            # means the project layer is not mounted on this machine, not a
            # broken contract. Any other dangling symlink is a real defect.
            if "mt-skills" in child.readlink().parts:
                unmounted.add(child.name)
                print(f"warn: unmounted mt-skills skill {child.name}")
            else:
                fail(f"BROKEN SYMLINK: {child}")
    return files, unmounted


skill_files, unmounted_skills = collect_skills()
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

MUST_BE_RETIRED = (
    "brainstorming", "systematic-debugging",
    "planning-in", "planning-in-remove", "planning-in-status",
    "planning-organize", "planning-review", "planning-split",
)
for retired in MUST_BE_RETIRED:
    if (SKILLS_DIR / retired).exists():
        fail(f"LEGACY MOVE INCOMPLETE: skills/{retired} still exists")
    if not (LEGACY_DIR / retired / "SKILL.md").exists():
        fail(f"LEGACY SKILL MISSING: legacy/{retired}/SKILL.md")
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
stale = sorted(referenced - skill_names - unmounted_skills)
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

link_re = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
url_prefixes = ("http://", "https://", "mailto:", "ftp://", "tel:", "data:")
for path in md_files:
    # Lark skills are vendored upstream; their references contain doc placeholders
    # like `img_xxx` and example URLs that are not real local links.
    if any(part.startswith("lark-") for part in path.parts):
        print(f"ok: markdown links {path}")
        continue
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
    # Lark skills are vendored upstream; skip table pipe checks on their content.
    if any(part.startswith("lark-") for part in path.parts):
        print(f"ok: table pipes {path}")
        continue
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

summary = f"verified {len(skill_files)} active skills"
if unmounted_skills:
    summary += f" ({len(unmounted_skills)} mt-skills skills unmounted)"
print(summary)
PYEOF
