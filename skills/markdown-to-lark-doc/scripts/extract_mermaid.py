#!/usr/bin/env python3
"""
extract_mermaid.py — Scan a markdown file, extract every ```mermaid fenced
block, and emit a processed copy with each fence replaced by:

    <whiteboard type="blank" data-mmd-id="N"></whiteboard>

Outputs:
    <input>.processed.md       — the rewritten markdown, suitable for
                                 `lark-cli docs +create/+update --doc-format
                                 markdown --content @<file>.processed.md`
    <input>.mermaid_blocks.json — JSON array; each item:
                                 {id, code, fence_lang, line_start, line_end}

Notes:
- Fences inside ```` ``` ```` outer code blocks are still extracted; we
  intentionally do not try to detect nested cases (lark-doc's markdown
  parser would render the inner ``` as plain text anyway).
- Only the lowercase ```mermaid``` opener is treated as mermaid. ```MMD``` /
  ```mermaidjs``` etc. are NOT extracted — explicit by design.
- Whitespace before the fence is preserved on the placeholder line.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FENCE_RE = re.compile(
    r"^(?P<indent>[ \t]*)```mermaid[ \t]*\r?\n"
    r"(?P<code>.*?)"
    r"^(?P=indent)```[ \t]*$",
    re.MULTILINE | re.DOTALL,
)


def extract(md_text: str):
    blocks = []
    out_parts = []
    last_end = 0
    next_id = 0

    for m in FENCE_RE.finditer(md_text):
        out_parts.append(md_text[last_end : m.start()])
        indent = m.group("indent")
        code = m.group("code").rstrip("\n")
        line_start = md_text.count("\n", 0, m.start()) + 1
        line_end = md_text.count("\n", 0, m.end()) + 1
        placeholder = (
            f'{indent}<whiteboard type="blank" data-mmd-id="{next_id}"></whiteboard>'
        )
        out_parts.append(placeholder)
        blocks.append(
            {
                "id": next_id,
                "code": code,
                "fence_lang": "mermaid",
                "line_start": line_start,
                "line_end": line_end,
            }
        )
        next_id += 1
        last_end = m.end()

    out_parts.append(md_text[last_end:])
    return "".join(out_parts), blocks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("input", help="Path to source markdown file")
    parser.add_argument(
        "--processed",
        help="Output path for processed markdown (default: <input>.processed.md)",
    )
    parser.add_argument(
        "--blocks",
        help="Output path for mermaid blocks JSON (default: <input>.mermaid_blocks.json)",
    )
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"error: input not found: {src}", file=sys.stderr)
        return 2

    md_text = src.read_text(encoding="utf-8")
    processed, blocks = extract(md_text)

    out_md = Path(args.processed) if args.processed else src.with_suffix(
        src.suffix + ".processed.md" if src.suffix != ".md" else ""
    )
    if not args.processed and src.suffix == ".md":
        out_md = src.with_name(src.stem + ".processed.md")

    out_json = (
        Path(args.blocks)
        if args.blocks
        else src.with_name(src.stem + ".mermaid_blocks.json")
    )

    out_md.write_text(processed, encoding="utf-8")
    out_json.write_text(
        json.dumps(blocks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "processed_md": str(out_md),
                "blocks_json": str(out_json),
                "block_count": len(blocks),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
