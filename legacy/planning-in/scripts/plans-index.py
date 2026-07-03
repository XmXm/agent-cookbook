#!/usr/bin/env python3
"""
plans-index.py — Maintain .plans/_index.json as a cache of plan metadata.

The index is ALWAYS derivable from disk. If it goes missing or stale, just
`rebuild`. Other skills should treat it as a fast-path; fall back to scanning
.plans/ if the index is unreadable.

Schema (version 1):
    {
      "version": 1,
      "updated_at": "<ISO8601 UTC>",
      "plans": [
        {
          "num": "001",
          "slug": "refactor",
          "dir": ".plans/001-refactor",
          "title": "API Refactor",
          "current_phase": "Phase 4",
          "phases_total": 5,
          "phases_complete": 3,
          "phases_in_progress": 1,
          "phases_failed": 0,
          "status": "in_progress",      # aggregate: pending|in_progress|complete|blocked
          "errors_logged": 2,
          "files": {"task_plan": 120, "findings": 45, "progress": 80},
          "created_at": "<ISO8601 UTC>",  # mtime of task_plan.md when first indexed
          "updated_at": "<ISO8601 UTC>"   # latest mtime among the three files
        }
      ]
    }

Usage:
    plans-index.py rebuild [--root .plans]      # scan disk, regenerate index
    plans-index.py sync <plan-dir>              # update one plan entry
    plans-index.py remove <plan-dir>            # drop one plan entry
    plans-index.py show [--root .plans]         # print index JSON
    plans-index.py dashboard [--root .plans]    # print human-readable dashboard
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INDEX_VERSION = 1
STATUS_ICONS = {
    "pending": "⏸️",
    "in_progress": "🔄",
    "complete": "✅",
    "failed": "❌",
    "blocked": "❌",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def mtime_iso(p: Path) -> str:
    return datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def line_count(p: Path) -> int:
    if not p.exists():
        return 0
    try:
        with p.open("r", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def parse_task_plan(path: Path) -> dict[str, Any]:
    """Extract title, current_phase, phase status counts, error count from task_plan.md."""
    title = ""
    current_phase = ""
    phase_statuses: list[str] = []
    errors_logged = 0

    if not path.exists():
        return {
            "title": "",
            "current_phase": "",
            "phases_total": 0,
            "phases_complete": 0,
            "phases_in_progress": 0,
            "phases_failed": 0,
            "errors_logged": 0,
        }

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    # Title: first "# " heading
    for line in lines:
        m = re.match(r"^# +(.+?)\s*$", line)
        if m:
            t = m.group(1).strip()
            # Strip "Task Plan:" prefix if present
            t = re.sub(r"^Task Plan:\s*", "", t, flags=re.IGNORECASE)
            title = t
            break

    # Current Phase: line right after "## Current Phase"
    for i, line in enumerate(lines):
        if re.match(r"^## +Current Phase\s*$", line):
            for j in range(i + 1, min(i + 5, len(lines))):
                v = lines[j].strip()
                if v and not v.startswith("#"):
                    current_phase = v
                    break
            break

    # Walk phases: each "### Phase N:" section, find the **Status:** line within
    phase_re = re.compile(r"^### +Phase\b")
    status_re = re.compile(r"\*\*Status:\*\*\s*([A-Za-z_]+)", re.IGNORECASE)
    section_idxs = [i for i, l in enumerate(lines) if phase_re.match(l)]
    for k, start in enumerate(section_idxs):
        end = section_idxs[k + 1] if k + 1 < len(section_idxs) else len(lines)
        section = "\n".join(lines[start:end])
        m = status_re.search(section)
        if m:
            phase_statuses.append(m.group(1).lower())
        else:
            phase_statuses.append("pending")

    # Errors Encountered: count data rows in the table after the heading
    err_idx = None
    for i, line in enumerate(lines):
        if re.match(r"^## +Errors? Encountered\s*$", line, re.IGNORECASE):
            err_idx = i
            break
    if err_idx is not None:
        # Count rows that look like markdown table data rows (start with `|`),
        # skipping the header and the `|---|` separator.
        seen_separator = False
        for line in lines[err_idx + 1 :]:
            s = line.strip()
            if s.startswith("##"):
                break
            if not s.startswith("|"):
                continue
            if re.match(r"^\|[\s\-:|]+\|\s*$", s):
                seen_separator = True
                continue
            if not seen_separator:
                # this is the header row
                continue
            # data row — must contain at least one non-empty cell
            cells = [c.strip() for c in s.strip("|").split("|")]
            if any(cells):
                errors_logged += 1

    return {
        "title": title,
        "current_phase": current_phase,
        "phases_total": len(phase_statuses),
        "phases_complete": sum(1 for s in phase_statuses if s == "complete"),
        "phases_in_progress": sum(1 for s in phase_statuses if s == "in_progress"),
        "phases_failed": sum(1 for s in phase_statuses if s in ("failed", "blocked")),
        "errors_logged": errors_logged,
    }


def aggregate_status(parsed: dict[str, Any]) -> str:
    total = parsed["phases_total"]
    if total == 0:
        return "pending"
    if parsed["phases_failed"] > 0:
        return "blocked"
    if parsed["phases_complete"] == total:
        return "complete"
    if parsed["phases_in_progress"] > 0 or parsed["phases_complete"] > 0:
        return "in_progress"
    return "pending"


def split_num_slug(dirname: str) -> tuple[str, str]:
    m = re.match(r"^(\d+)-(.+)$", dirname)
    if m:
        return m.group(1), m.group(2)
    return "", dirname


def canonical_dir(plan_dir: Path, index_root: Path) -> str:
    """Canonical 'dir' field: '<root_basename>/<plan_basename>' (e.g. '.plans/001-demo').

    Stable regardless of whether caller passed absolute or relative paths, and
    regardless of CWD. Matches how users normally write paths in commands.
    """
    return f"{index_root.name}/{plan_dir.name}"


def build_entry(
    plan_dir: Path,
    index_root: Path,
    existing_created: str | None = None,
) -> dict[str, Any]:
    task_plan = plan_dir / "task_plan.md"
    findings = plan_dir / "findings.md"
    progress = plan_dir / "progress.md"

    parsed = parse_task_plan(task_plan)
    num, slug = split_num_slug(plan_dir.name)

    files = {
        "task_plan": line_count(task_plan),
        "findings": line_count(findings),
        "progress": line_count(progress),
    }

    mtimes = [p for p in (task_plan, findings, progress) if p.exists()]
    updated_at = (
        max(mtime_iso(p) for p in mtimes) if mtimes else now_iso()
    )

    if existing_created:
        created_at = existing_created
    elif task_plan.exists():
        created_at = mtime_iso(task_plan)
    else:
        created_at = now_iso()

    return {
        "num": num,
        "slug": slug,
        "dir": canonical_dir(plan_dir, index_root),
        "title": parsed["title"] or plan_dir.name,
        "current_phase": parsed["current_phase"],
        "phases_total": parsed["phases_total"],
        "phases_complete": parsed["phases_complete"],
        "phases_in_progress": parsed["phases_in_progress"],
        "phases_failed": parsed["phases_failed"],
        "status": aggregate_status(parsed),
        "errors_logged": parsed["errors_logged"],
        "files": files,
        "created_at": created_at,
        "updated_at": updated_at,
        "stale": not task_plan.exists(),
    }


def discover_plan_dirs(root: Path) -> list[Path]:
    """Return all immediate subdirs of root, excluding 'archive' and 'active' staging dirs."""
    if not root.exists():
        return []
    out = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name in ("archive", "active"):
            continue
        if child.name.startswith("_"):
            continue
        out.append(child)
    return out


def load_index(index_path: Path) -> dict[str, Any]:
    if not index_path.exists():
        return {"version": INDEX_VERSION, "updated_at": now_iso(), "plans": []}
    try:
        return json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"version": INDEX_VERSION, "updated_at": now_iso(), "plans": []}


def save_index(index_path: Path, data: dict[str, Any]) -> None:
    data["version"] = INDEX_VERSION
    data["updated_at"] = now_iso()
    # Sort plans by num (numeric where possible), then slug
    def sort_key(p: dict[str, Any]) -> tuple[int, str]:
        try:
            return (int(p.get("num") or 0), p.get("slug", ""))
        except ValueError:
            return (0, p.get("slug", ""))

    data["plans"] = sorted(data.get("plans", []), key=sort_key)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def cmd_rebuild(args: argparse.Namespace) -> int:
    root = Path(args.root)
    index_path = root / "_index.json"
    existing = {p["dir"]: p for p in load_index(index_path).get("plans", [])}

    plans = []
    for d in discover_plan_dirs(root):
        key = canonical_dir(d, root)
        prev = existing.get(key)
        prev_created = prev["created_at"] if prev else None
        plans.append(build_entry(d, root, existing_created=prev_created))

    data = {"version": INDEX_VERSION, "updated_at": now_iso(), "plans": plans}
    save_index(index_path, data)
    print(f"Rebuilt {index_path} ({len(plans)} plans).")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    plan_dir = Path(args.plan_dir)
    if not plan_dir.exists() or not plan_dir.is_dir():
        print(f"Error: {plan_dir} is not a directory.", file=sys.stderr)
        return 1

    # Index lives in the parent of the plan dir
    root = plan_dir.parent
    index_path = root / "_index.json"
    data = load_index(index_path)
    plans = data.get("plans", [])

    key = canonical_dir(plan_dir, root)
    existing_created = None
    found = -1
    for i, p in enumerate(plans):
        if p.get("dir") == key:
            found = i
            existing_created = p.get("created_at")
            break

    entry = build_entry(plan_dir, root, existing_created=existing_created)
    if found >= 0:
        plans[found] = entry
    else:
        plans.append(entry)

    data["plans"] = plans
    save_index(index_path, data)
    print(f"Synced {key} → {index_path}")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    plan_dir = Path(args.plan_dir)
    # Index lives in the parent (use given path even if dir already deleted)
    root = plan_dir.parent if str(plan_dir.parent) else Path(".plans")
    index_path = root / "_index.json"

    data = load_index(index_path)
    plans = data.get("plans", [])
    key = canonical_dir(plan_dir, root)
    new_plans = [p for p in plans if p.get("dir") != key]

    if len(new_plans) == len(plans):
        print(f"No entry for {key} in {index_path}.")
        return 0

    data["plans"] = new_plans
    save_index(index_path, data)
    print(f"Removed {key} from {index_path}.")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    root = Path(args.root)
    index_path = root / "_index.json"
    data = load_index(index_path)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


def cmd_dashboard(args: argparse.Namespace) -> int:
    root = Path(args.root)
    index_path = root / "_index.json"

    # Always rebuild before showing dashboard so output is fresh.
    if not args.no_rebuild:
        existing = {p["dir"]: p for p in load_index(index_path).get("plans", [])}
        plans_data = []
        for d in discover_plan_dirs(root):
            key = canonical_dir(d, root)
            prev = existing.get(key)
            prev_created = prev["created_at"] if prev else None
            plans_data.append(build_entry(d, root, existing_created=prev_created))
        save_index(index_path, {"version": INDEX_VERSION, "plans": plans_data})

    data = load_index(index_path)
    plans = data.get("plans", [])

    if not plans:
        print("No active plans. Use /planning-in <name> to create one.")
        return 0

    active = [p for p in plans if p.get("status") != "complete" and not p.get("stale")]
    completed = [p for p in plans if p.get("status") == "complete"]
    stale = [p for p in plans if p.get("stale")]

    print(f"Plans ({len(plans)} total · {len(active)} active · "
          f"{len(completed)} complete · {len(stale)} stale):\n")

    def render_one(p: dict[str, Any]) -> None:
        icon = STATUS_ICONS.get(p.get("status", "pending"), "·")
        title = p.get("title") or p.get("slug", "")
        cur = p.get("current_phase", "")
        cp = p.get("phases_complete", 0)
        tt = p.get("phases_total", 0)
        slug_label = f"{p.get('num','')}-{p.get('slug','')}".strip("-")
        head = f"  [{slug_label}] {p.get('dir','')}"
        print(head)
        print(f"    {title} — Phase {cp}/{tt} ({icon} {p.get('status','')})")
        if cur:
            print(f"    current: {cur}")
        files = p.get("files", {})
        print(
            f"    files: task_plan({files.get('task_plan',0)}L) "
            f"findings({files.get('findings',0)}L) "
            f"progress({files.get('progress',0)}L)"
        )
        if p.get("errors_logged"):
            print(f"    errors logged: {p['errors_logged']}")
        print(f"    updated: {p.get('updated_at','')}")
        print()

    if active:
        print("── Active ──")
        for p in active:
            render_one(p)
    if completed:
        print("── Completed ──")
        for p in completed:
            render_one(p)
    if stale:
        print("── Stale (no task_plan.md) ──")
        for p in stale:
            print(f"  [{p.get('num','')}-{p.get('slug','')}] {p.get('dir','')}")
        print("\n  Use /planning-in-remove to clean up stale directories.")

    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Maintain .plans/_index.json")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_rebuild = sub.add_parser("rebuild", help="Scan disk, regenerate index")
    p_rebuild.add_argument("--root", default=".plans")
    p_rebuild.set_defaults(func=cmd_rebuild)

    p_sync = sub.add_parser("sync", help="Update one plan entry")
    p_sync.add_argument("plan_dir")
    p_sync.set_defaults(func=cmd_sync)

    p_remove = sub.add_parser("remove", help="Drop one plan entry")
    p_remove.add_argument("plan_dir")
    p_remove.set_defaults(func=cmd_remove)

    p_show = sub.add_parser("show", help="Print index JSON")
    p_show.add_argument("--root", default=".plans")
    p_show.set_defaults(func=cmd_show)

    p_dash = sub.add_parser("dashboard", help="Print human-readable dashboard")
    p_dash.add_argument("--root", default=".plans")
    p_dash.add_argument("--no-rebuild", action="store_true",
                        help="Read existing index without re-scanning disk")
    p_dash.set_defaults(func=cmd_dashboard)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
