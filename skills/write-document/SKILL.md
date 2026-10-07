---
name: write-document
description: >-
  Writes, rewrites, polishes, and reviews documents and prose: design docs, weekly reports,
  postmortems, READMEs, runbooks, KB articles, release notes, social posts. Applies
  one-reading wording rules to technical text, cuts AI tone everywhere, and names the
  delivery route. Use when asked to write, draft, organize, polish, rewrite, review, or
  de-AI a document or copy（写文档、写周报、写设计文档、改稿、润色、去 AI 味、审稿）.
  Not for code comments or commit messages.
when_to_use: "写文档, 出文档, 写设计文档, 写周报, 整理成周报, 写复盘, 写 postmortem, 写 README, 写 KB 知识, 写知识文档, 写 runbook, 文档骨架, 改稿, 润色, 去AI味, 去翻译腔, 写得干净点, 审稿, 文档review, 改技术文档, 发布说明, changelog, 回复 issue, 推特, 推文, 段落连贯, 本地化文案, write a design doc, weekly report, postmortem, knowledge article, draft a doc, polish, rewrite, proofread, edit text, clarify instructions, release notes, tweet"
dispatch_intent: "Document creation, rewrite, polish, review; remove AI tone; technical wording; weekly report, design doc, postmortem, release notes, social copy"
---

# Write-Document: Documents and Prose With One Reading

Create a document from raw material, rewrite or polish existing text, or review
it. Technical text follows the wording rules in the style files; every text gets
the AI-tone pass in the polish files. This skill owns the whole writing door;
there is no separate polish skill.

## Outcome Contract

- Outcome: text the reader can read one way only, in the author's voice, with every
  fact of the source intact, ready for its delivery channel.
- Done when: the mode's scope is met; facts, conditions, risks, and uncertainty
  survive; hard wording rules hold for technical text; `scripts/check.py` leaves no
  unexplained hard hit; the delivery route is named.
- Evidence: source material (conversation, files, code, data), audience, channel,
  project glossary and style guide.
- Output: see [Output](#output).

## Modes

| Ask | Mode | Default scope |
|---|---|---|
| Material to a new doc ("写设计文档", "整理成周报", "draft a postmortem") | Create | Pick the type skeleton, fill from sources |
| Existing text to improve ("改稿", "润色", "去 AI 味", "写得干净点", "rewrite") | Rewrite | Line-level edits in place; sections, headings, links, facts unchanged |
| Find problems without editing ("审稿", "文档 review", "check this document") | Review | Findings only; load the Document Review section of `references/modes.md` |
| Release note, changelog, public issue/PR reply, tweet or social post, long draft needing structural work, bilingual or localization copy, paragraph coherence | Special | Load `references/modes.md` and follow the matching section |

The author's own finished draft shrinks Rewrite to typos, broken sentences, and
clear AI tells. Return a per-sentence list of every deleted or rewritten
sentence so the author can veto each one.

## Scope of the Rule Sets

| Text | Style rules | Polish |
|---|---|---|
| Technical: design doc, README, runbook, API doc, troubleshooting, migration guide, error text, weekly report, postmortem, KB | yes | yes |
| Persuasive or personal: social post, launch announcement, blog, speech, essay | no (it flattens rhythm) | yes |
| Mixed: release notes, announcements | technical parts only (what changed, how to upgrade, what breaks) | yes |

- Load by the language of the text, not the conversation: `references/style-zh.md`
  and `references/polish-zh.md` for Chinese, `references/style-en.md` and
  `references/polish-en.md` for English. A bilingual text uses both sets, each on
  its own part.
- If the user asks for style rules on persuasive text, apply them and say once
  that the text will lose its persuasive tone.
- Translation is not this skill's job. Translate first, then apply the target
  language's rules.
- Rule files are catalogs, not checklists. Applying more rules is not a better job.

## Rule Priority & Fact Fidelity

<!-- Distilled from Fenng/Tech-Doc-Style-Chinese (MIT) and the meaning checks of
     tw93/Waza write-technical (MIT), idea reuse, no dependency. -->

When rules conflict, never sacrifice a higher level for a lower one (e.g. never
drop a caveat to make a sentence shorter):

1. Facts, constraints, safety and risk information.
2. Explicit user instructions and target-project conventions.
3. Terminology and machine-readable content accuracy.
4. Structure, tone, and scannability.
5. Punctuation, spacing, and typography.

Fact fidelity:

- Do not invent dates, numbers, deadlines, SLAs, capabilities, or conclusions.
- Do not drop preconditions, exceptions, risks, warnings, units, or defaults when condensing.
- Keep obligation and certainty at the source's strength: 应 / 宜 / 可 / 能 and
  "可能 / 通常 / 计划" stay as written; completed, started, and planned work stay distinct.
- Keep each condition attached to the action it governs; necessary and sufficient
  conditions do not swap ("只有校验通过才重启" is not "校验通过就重启").
- Keep observation, possible cause, and remedy apart; never add a remedy the source
  does not support.

## Hard Rules

- **Meaning first, style second.** If removing a smell would change the meaning, keep the original.
- **Wording, not content.** Rewrite and Review add no facts or requirements. A missing
  risk, rollback, or condition the reader needs becomes a note for the author.
- **Rewriting is not auditing.** Keep each claim at its written strength; drop only
  empty intensifiers ("显著提升" to "提升", "improved significantly" to "improved").
- **Gaps go to the author, not the page.** Write an inline 「待确认：……」 only when the
  reader cannot act without the fact, or when a Create-mode section has no source at
  all. List every other gap (unmeasured claim, missing condition, missing evidence)
  under 给作者. Never put a guess or a plausible number in a placeholder.
- **No silent restructuring.** Rewrite keeps sections, headings, order, links, images,
  frontmatter, and examples. Structural changes happen only when requested, and every
  removal is listed with its reason.
- **Over-editing is a failure equal to under-editing.** A clear, natural sentence stays.
  Prefer a few strong edits to many mechanical swaps.
- **Leave what must stay:** quotations, code, command output, proper names, UI labels,
  and the user's own words.
- **No invented first-person experience.** Anecdotes, opinions, and quotes come from
  the supplied material or the author's published writing. Fix by subtraction.
- **Material gate before long drafts.** Count real materials (experience, numbers,
  quotes, actions, verifiable sources) before choosing a length. Each planned section
  needs a distinct material; otherwise research, ask at most three questions in one
  round, or ship shorter. A word count is never a reason to pad.
- **Artifact-grounded outward copy.** Release notes, social posts, public replies, and
  product pages match the shipping artifact. Plans, handoffs, and old memory are not
  current product truth.
- **Deliver a finished draft.** No "here's a starting point, expand as needed".

## Workflow

1. **Preflight.** Run `shared/knowledge-preflight.md`: nmem for document-type
   conventions and prior examples; the project KB per `shared/project-routing.md`
   when mounted and in Scope. Find the project glossary and style guide (chapter 10
   of the style files); project conventions beat these rules. Read Feishu documents
   with `/lark-doc` (WebFetch has no Feishu login). If a source is unavailable, say so
   and proceed.
2. **Lock mode, type, audience, channel.** Infer the type from the request. Ask only
   when two types are plausible and a wrong pick is costly, or when an unclear
   audience would change the register.
3. **Gather sources (Create).** Conversation, named files, `git log` since the last
   report, nmem. Project-specific sources come from the `write-document: Source
   Signals` section of `shared/project-routing.md` when mounted and in Scope.
4. **Write or edit.** Use the type skeleton below and the rule files for the language.
5. **Check.** Run `python3 <skill-dir>/scripts/check.py <file>` (`-` reads stdin;
   `--lang zh|en` forces a language). Hits are places to read, not verdicts:
   quoted examples, names next to code, and soft rules kept for a reason stay. Then
   do the judgment pass the script cannot: term drift (1.1), missing subject (4.2),
   ambiguous pronoun (4.3), conclusion first (6.1), done versus planned (6.5), and
   the smells in the polish file.
6. **Deliver** per [Output](#output).

## Document Types

### README

The top answers "what is this and how do I use it" within 30 seconds of reading.

### Design Doc

Goal → Building / Not Building → Approach → Key Decisions → Risks → Verification.
Same headers as `/plan` output, written as a standalone document.

### Postmortem

Incident summary → Timeline → Root cause → Impact → Fix → Lessons → Action items
(owner + deadline). Blameless: system failures, not individual mistakes. State a
root cause as certain only when evidence supports it; otherwise write 可能原因 and
name the missing evidence.

### Runbook / Operation Guide

Procedures follow chapter 5 of the style files and warnings follow chapter 7 in
full: numbered steps, imperative verbs, condition before instruction, warning
before the step it governs.

### Weekly Report (飞书周进展)

Structure: 概述 → 画板 (optional) → 主要进展 → 后续安排.

- Start each item with a verb that says what was done: "完成了 X 的联调", "修复了 Y 的同步问题".
- 主要进展 holds only what happened, in completed form; anything planned
  ("将会 / 准备 / 计划") goes to 后续安排.
- Group by topic, not by 一二三 numbered sections.
- Keep each progress item to 1-2 sentences.

### KB Knowledge Article

Route to the knowledge-writeback skill declared in `shared/project-routing.md`
(if mounted); it owns the KB frontmatter contract. This skill provides the
structure and wording. No routing table → write a plain markdown knowledge note.

### Delivery Routes

- Feishu: `/markdown-to-lark-doc` for whole-file import with mermaid → 画板;
  `/lark-doc` for direct editing.
- Notion: `/notion-md-sync`.
- Project main doc: the main-doc skill declared in `shared/project-routing.md`
  (if mounted); otherwise a design doc in local markdown.

## Structure Discipline

- Same fact in two sections: keep it in one, reference it from the other.
- Do not repeat table data in surrounding prose.
- No vague referents: replace "几个方向 / 一些问题 / 这些东西" with a counted, exact
  category noun ("三类风险", "两个待决项").
- Before deleting a section, confirm its information lives elsewhere.
- Markdown: escape `|` in table cells; wrap Mermaid node text with `<br/>`, not `\n`.

## Gotchas

| What happened | Rule |
|---|---|
| Wrote a README when asked to "write about X" | Infer the type from the request; for a technical topic default to a design doc and say so |
| Weekly report had numbered lists 1/2/3 | Use natural topic grouping |
| KB article missing frontmatter | Route KB knowledge to the writeback skill in `shared/project-routing.md` |
| Every unmeasured claim became an inline 待确认 and the doc read like a gap list | Inline placeholders only for facts the reader cannot act without; the rest goes to 给作者 |
| Applied style rules to a launch tweet and it went flat | Persuasive text gets polish only |
| Script flagged a quoted example or a term next to code | A hit is a place to read; leave it and move on |
| Rewrote the author's finished draft for style | Shrink to typos, broken sentences, and clear AI tells; return a per-sentence change list |

## Output

- **Files:** edit in place only when the user targeted that file and it is under
  version control; otherwise write a clearly named sibling file.
- **Pasted text:** return the edited text without explanation, except the
  per-sentence change list for an author's own finished draft.
- **After a Create or Rewrite of a document,** add a short note and omit empty parts:
  - 交付路由: Feishu / Notion / KB / local.
  - 检查: hard hits left by `scripts/check.py` and why each stays.
  - 给作者: claims kept without data, 待确认 items and where they are, risks the
    rules cannot fix, and a proposed glossary when the project has none.
- **Review:** a findings table with hard-rule findings first; quote the original
  exactly and give a suggestion the author can paste. End with one line: hard and
  soft counts, and whether a project glossary was followed or none was found.

```markdown
| 位置 | 规则 | 原文 | 建议 |
|---|---|---|---|
| 第 12 行 | 3.1 硬 | 对日志进行压缩处理 | 压缩日志 |
```
