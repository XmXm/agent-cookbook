#!/usr/bin/env python3
"""Skill usage observability across Claude Code transcripts. Read-only.

Scans ~/.claude/projects/*/*.jsonl for Skill tool_use blocks and reports
invocation counts, front-door coverage, and per-project breakdown. This
establishes the observation baseline for skill routing; it counts
invocations only.

Explicit gaps (reported, never silent):
- Codex sessions are not parsed (different log format).
- Routing quality (hit / miss / misfire) needs judgment, not counting;
  pair this output with periodic manual or agent-assisted review.
"""

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

FRONT_DOORS = ("plan", "check", "hunt", "write-document", "cs-coding")


def parse_args():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--days", type=int, default=30,
                   help="recent window in days (default: 30)")
    p.add_argument("--projects-dir", type=Path,
                   default=Path.home() / ".claude" / "projects")
    return p.parse_args()


def iter_skill_calls(jsonl_path):
    """Yield (timestamp_iso, skill_name) for every Skill tool_use in a session."""
    with open(jsonl_path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("type") != "assistant":
                continue
            content = (d.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if (isinstance(block, dict)
                        and block.get("type") == "tool_use"
                        and block.get("name") == "Skill"):
                    skill = (block.get("input") or {}).get("skill")
                    if skill:
                        yield d.get("timestamp"), skill


def main():
    args = parse_args()
    if not args.projects_dir.is_dir():
        raise SystemExit(f"projects dir not found: {args.projects_dir}")

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)

    total = Counter()
    recent = Counter()
    per_project_doors = defaultdict(Counter)
    sessions_total = 0
    sessions_with_skill = 0
    sessions_with_door = 0
    parse_failures = []

    for proj in sorted(p for p in args.projects_dir.iterdir() if p.is_dir()):
        try:
            session_files = sorted(proj.glob("*.jsonl"))
        except OSError as exc:
            parse_failures.append(f"{proj}: {exc}")
            continue
        for f in session_files:
            sessions_total += 1
            saw_skill = saw_door = False
            try:
                for ts, skill in iter_skill_calls(f):
                    saw_skill = True
                    total[skill] += 1
                    in_window = False
                    if ts:
                        try:
                            when = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                            if when.tzinfo is None:
                                when = when.replace(tzinfo=timezone.utc)
                            in_window = when >= cutoff
                        except (ValueError, TypeError):
                            pass
                    if in_window:
                        recent[skill] += 1
                    if skill in FRONT_DOORS:
                        saw_door = True
                        per_project_doors[proj.name][skill] += 1
            except OSError as exc:
                parse_failures.append(f"{f}: {exc}")
                continue
            sessions_with_skill += saw_skill
            sessions_with_door += saw_door

    print(f"# Skill usage — all time vs last {args.days} days\n")
    print(f"{'skill':<28} {'all':>5} {'recent':>7}")
    for skill, n in total.most_common():
        marker = " *" if skill in FRONT_DOORS else ""
        print(f"{skill:<28} {n:>5} {recent.get(skill, 0):>7}{marker}")
    print("\n(* = front door)")

    print(f"\n# Front-door coverage")
    print(f"sessions scanned:            {sessions_total}")
    print(f"sessions with any skill:     {sessions_with_skill}")
    print(f"sessions with a front door:  {sessions_with_door}")

    print(f"\n# Front doors by project (all time)")
    for proj, counts in sorted(per_project_doors.items(),
                               key=lambda kv: -sum(kv[1].values())):
        row = ", ".join(f"{s}:{n}" for s, n in counts.most_common())
        print(f"{proj:<44} {row}")

    if parse_failures:
        print(f"\n# Unreadable session files ({len(parse_failures)})")
        for line in parse_failures:
            print(f"  {line}")

    print("\n# Not covered: Codex sessions; routing hit/miss/misfire judgment.")


if __name__ == "__main__":
    main()
