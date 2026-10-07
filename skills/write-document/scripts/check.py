#!/usr/bin/env python3
"""Mechanical wording check for write-document.

Usage:
  python3 check.py [--lang auto|zh|en] FILE [FILE ...]
  python3 check.py [--lang auto|zh|en] -          # read stdin

Rule numbers refer to references/style-zh.md and references/style-en.md,
which share one numbering. With --lang auto (default) a line that contains a
Han character is checked with the Chinese rules, any other line with the
English rules.

Skipped: YAML frontmatter, fenced code blocks, inline code, URLs, Markdown
link targets, HTML comments, and table separator rows. Word rules also skip
text inside quotation marks, which usually holds an example, not a claim.

A hit is a place to read, not a verdict: quoted examples, names next to code,
and soft rules kept for a reason can stay.

Output: one line per rule per source line
  path:line: [rule level] message: snippet
followed by a summary line. Exit status 1 if any hard hit, else 0.
Standard library only; Python 3.8+.
"""
from __future__ import annotations

import argparse
import re
import sys
from typing import Iterable, List, Pattern, Tuple

HAN = "[\u3400-\u4dbf\u4e00-\u9fff]"
DASH = r"\u2014|(?<!\d)\u2013|\u2013(?!\d)"  # em dash anywhere; en dash outside numeric ranges

Rule = Tuple[str, str, str, Pattern[str]]


def rules(specs: Iterable[Tuple[str, str, str, str, int]]) -> List[Rule]:
    return [(num, level, msg, re.compile(pat, flags)) for num, level, msg, pat, flags in specs]


# Word rules run on text with quoted spans removed.
ZH_WORD = rules([
    ("1.4", "hard", "含糊词，写成数字、名称或条件",
     r"适当|有关的|一定程度上?|较为|基本上|若干|显著|大幅|明显", 0),
    ("3.1", "hard", "包装动词，把名词改回动词",
     r"进行|加以|予以|做出|实现了?对[^。；，]{1,20}的支持", 0),
    ("3.3", "soft", "陈述事实不用“正在”", r"正在", 0),
    ("3.4", "hard", "表达要求只用 应/不应/宜/不宜/可/不必（不是要求时可保留）",
     r"必须|务必|最好|尽量|建议", 0),
    ("9.4", "soft", "套话，写出具体做了什么",
     r"开箱即用|无缝|一劳永逸|飞跃|极致|赋能|抓手|闭环|全方位|强大的", 0),
    ("9.8", "soft", "AI 壳，删掉外壳直接写结论",
     r"不是[^。；！？\n]{1,30}?而是|真正|本质上|更重要的是|值得注意的是|总的来说|综上所述|不难发现", 0),
])
# Punctuation rules run on text with code and URLs removed, quotes kept.
ZH_PUNCT = rules([
    ("8.1", "hard", "中文旁用了半角标点", rf"{HAN}[,;:?!]|[,;:?!]{HAN}|{HAN}\(|\){HAN}", 0),
    ("8.3", "hard", "中文和英文、数字之间空一格", rf"{HAN}[A-Za-z0-9]|[A-Za-z0-9]{HAN}", 0),
    ("8.6", "hard", "范围用“–”或“到”，不用“~”", r"\d\s*[~～]\s*\d", 0),
    ("8.10", "hard", "不用破折号，改用逗号、句号、冒号或括号", DASH, 0),
])
EN_WORD = rules([
    ("1.4", "hard", "vague word: give a number, a name, or a condition",
     r"\b(?:appropriate(?:ly)?|relevant|various|significant(?:ly)?|substantial(?:ly)?"
     r"|fairly|quite|somewhat|basically|essentially)\b", re.I),
    ("3.1", "hard", "hidden verb: use the verb itself",
     r"\b(?:perform(?:s|ed|ing)?|carr(?:y|ies|ied|ying) out|conduct(?:s|ed|ing)?)\b", re.I),
    ("3.4", "hard", "requirement word: use must / must not / should / should not / can / need not",
     r"\b(?:needs? to|ha(?:s|ve) to|make sure|ensure that|try to|ideally|it is recommended)\b", re.I),
    ("9.4", "soft", "filler or marketing word: state the fact",
     r"\b(?:simply|just|easily|obviously|seamless(?:ly)?|leverag(?:e|es|ed|ing)|robust|powerful"
     r"|cutting-edge|best-in-class|out of the box)\b", re.I),
    ("9.8", "soft", "AI shell: state the claim directly",
     r"\b(?:it(?:'s| is) worth noting|delve|in essence|at its core|not (?:just|only) [^.;]{1,40}? but)\b", re.I),
])
EN_PUNCT = rules([
    ("8.6", "hard", "ranges use – or to, not ~", r"\d\s*~\s*\d", 0),
    ("8.10", "hard", "no em dash: use a comma, period, colon, or parentheses", DASH, 0),
])

FENCE = re.compile(r"^\s*(```|~~~)")
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
INLINE_CODE = re.compile(r"`[^`]*`")
URL = re.compile(r"https?://\S+")
LINK_TARGET = re.compile(r"\]\([^)]*\)")
HTML_COMMENT = re.compile(r"<!--.*?-->")
QUOTED = re.compile(r"“[^”]*”|\"[^\"]*\"|「[^」]*」|‘[^’]*’")
CLAUSE_SPLIT = re.compile(r"[，。；：！？,;:!?]")
HAS_HAN = re.compile(HAN)


def prose_lines(text: str) -> Iterable[Tuple[int, str]]:
    """Yield (line number, prose with code, URLs, and comments blanked out)."""
    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start = i + 1
                break
    in_fence = in_comment = False
    for idx in range(start, len(lines)):
        line = lines[idx]
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or TABLE_SEP.match(line):
            continue
        if in_comment:
            if "-->" not in line:
                continue
            line = line.split("-->", 1)[1]
            in_comment = False
        line = HTML_COMMENT.sub(" ", line)
        if "<!--" in line:
            line = line.split("<!--", 1)[0]
            in_comment = True
        line = INLINE_CODE.sub(" ", line)
        line = LINK_TARGET.sub("]", line)
        line = URL.sub(" ", line)
        yield idx + 1, line


def snippet(text: str, match: re.Match) -> str:
    return text[max(0, match.start() - 10): match.end() + 10].strip()


def check_text(text: str, path: str, lang: str) -> Tuple[List[str], int, int]:
    out: List[str] = []
    hard = soft = 0
    for lineno, line in prose_lines(text):
        is_zh = lang == "zh" or (lang == "auto" and HAS_HAN.search(line) is not None)
        unquoted = QUOTED.sub(" ", line)
        checks = [(r, unquoted) for r in (ZH_WORD if is_zh else EN_WORD)]
        checks += [(r, line) for r in (ZH_PUNCT if is_zh else EN_PUNCT)]
        hits: List[Tuple[str, str, str, str]] = []
        for (num, level, msg, pat), target in checks:
            found = list(pat.finditer(target))
            if found:
                extra = f" (×{len(found)})" if len(found) > 1 else ""
                hits.append((num, level, msg + extra, snippet(target, found[0])))
        if is_zh:
            for clause in CLAUSE_SPLIT.split(unquoted):
                if clause.count("的") >= 3:
                    hits.append(("2.1", "soft", "一个名词前最多两个“的”", clause.strip()))
                    break
        for num, level, msg, snip in hits:
            out.append(f"{path}:{lineno}: [{num} {level}] {msg}: {snip}")
            if level == "hard":
                hard += 1
            else:
                soft += 1
    return out, hard, soft


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Mechanical wording check for write-document.")
    parser.add_argument("--lang", choices=("auto", "zh", "en"), default="auto")
    parser.add_argument("files", nargs="+", help="files to check, or - for stdin")
    args = parser.parse_args(argv)

    total_hard = total_soft = 0
    for path in args.files:
        if path == "-":
            text, label = sys.stdin.read(), "<stdin>"
        else:
            with open(path, encoding="utf-8") as fh:
                text, label = fh.read(), path
        lines, hard, soft = check_text(text, label, args.lang)
        for line in lines:
            print(line)
        total_hard += hard
        total_soft += soft

    if total_hard or total_soft:
        print(f"check: {total_hard} hard, {total_soft} soft")
    else:
        print("check: ok")
    return 1 if total_hard else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
