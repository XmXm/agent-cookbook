#!/usr/bin/env python3
"""
stitch_boards.py — Align mermaid placeholders with whiteboard tokens returned
by `lark-cli docs +create/+update --api-version v2`.

Inputs:
    --blocks   <path>   mermaid_blocks.json from extract_mermaid.py
    --response <path>   raw JSON envelope from lark-cli docs +create/+update
                        (or pass `-` to read from stdin)
    --basename <name>   short label used in --idempotent-token (default: doc)
    --epoch    <int>    unix seconds to seed idempotent tokens
                        (default: time.time())

Behavior:
- Filters `data.document.new_blocks[]` where `block_type == "whiteboard"`.
- Pairs them positionally with the mermaid blocks (v2 server preserves the
  document-order of new blocks). If counts differ, exits non-zero with a
  message on stderr so the caller can stop and surface the discrepancy to
  the user.
- Emits a JSON array on stdout. Each item:
    {"mmd_id", "code", "board_token", "block_id", "idempotent_token"}
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path


TOKEN_RE = re.compile(r"^wb[a-zA-Z0-9]{10,}$")


def load_blocks(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_response(arg: str):
    if arg == "-":
        return json.load(sys.stdin)
    with open(arg, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_whiteboards(resp):
    data = resp.get("data", resp) if isinstance(resp, dict) else {}
    doc = data.get("document") if isinstance(data, dict) else None
    new_blocks = (
        doc.get("new_blocks", [])
        if isinstance(doc, dict)
        else data.get("new_blocks", []) if isinstance(data, dict) else []
    )
    whiteboards = [
        b
        for b in new_blocks
        if isinstance(b, dict) and b.get("block_type") == "whiteboard"
    ]
    return whiteboards


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--blocks", required=True)
    p.add_argument("--response", required=True, help="path to JSON, or '-' for stdin")
    p.add_argument("--basename", default="doc")
    p.add_argument("--epoch", type=int, default=None)
    args = p.parse_args()

    blocks = load_blocks(args.blocks)
    resp = load_response(args.response)

    if isinstance(resp, dict) and resp.get("ok") is False:
        err = resp.get("error") or {}
        print(
            f"error: lark-cli response indicates failure: "
            f"{err.get('message') or json.dumps(err)}",
            file=sys.stderr,
        )
        return 3

    whiteboards = extract_whiteboards(resp)

    if len(whiteboards) != len(blocks):
        print(
            f"error: count mismatch — mermaid placeholders={len(blocks)}, "
            f"whiteboard new_blocks={len(whiteboards)}. "
            f"Inspect response.data.document.new_blocks and the source markdown.",
            file=sys.stderr,
        )
        return 4

    epoch = args.epoch if args.epoch is not None else int(time.time())
    basename = re.sub(r"[^A-Za-z0-9_-]+", "-", args.basename).strip("-") or "doc"

    out = []
    for i, (blk, wb) in enumerate(zip(blocks, whiteboards)):
        token = wb.get("block_token") or ""
        if not TOKEN_RE.match(token):
            print(
                f"warning: board_token #{i} looks unusual: {token!r}",
                file=sys.stderr,
            )
        idempotent = f"{epoch}-{basename}-{i}"
        if len(idempotent) < 10:
            idempotent = (idempotent + "-padding")[:16]
        out.append(
            {
                "mmd_id": blk["id"],
                "code": blk["code"],
                "board_token": token,
                "block_id": wb.get("block_id", ""),
                "idempotent_token": idempotent,
            }
        )

    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
