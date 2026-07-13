---
name: write-document
description: >-
  Structured document creation: README, design docs, postmortems, weekly reports, KB
  knowledge articles, and Feishu delivery. Use when users ask to write, draft, or organize
  a structured document, weekly progress report, design doc, postmortem, or KB knowledge
  article. Not for prose polish/rewrite (use write), code comments, or commit messages.
when_to_use: "写设计文档, 写文档, 整理成周报, 写周报, 写 KB 知识, 写 postmortem, 写 README, 写知识文档, 出文档, 文档骨架, write a design doc, write documentation, weekly report, postmortem, knowledge article, draft a doc, organize into a doc"
dispatch_intent: "Structured document creation, weekly report, design doc, postmortem, KB knowledge, README"
---

# Write-Document: Create Structured Documents

Create well-structured documents from scratch or from raw material. Each
document type has a skeleton and delivery route. This skill creates and
structures; it does not polish prose or remove AI tone — route deep polish to
`/write`.

## Outcome Contract

- Outcome: a structured document matching the requested type, ready for its delivery channel.
- Done when: the document has the correct skeleton, all sections are filled (no TBD), and the delivery route is named.
- Evidence: source material (conversation, code, data), target audience, and delivery channel.
- Output: the document file, plus the delivery route if applicable.

## Knowledge Preflight

Before drafting, run the preflight defined in `shared/knowledge-preflight.md`:
search nmem for document-type conventions and prior examples; search the
project KB (per `shared/project-routing.md`, if mounted and the document falls
within its declared Scope) when the document touches its domain. To reference an existing Feishu document, use `/lark-doc`
to read it (WebFetch has no Feishu login). If sources are unavailable, state
so and proceed.

## Document Types

### README

- Purpose → audience → quick start → architecture (brief) → contributing.
- Keep the reader from scrolling: the top should answer "what is this and how
  do I use it" in under 30 seconds.

### Design Doc

- Goal → Building / Not Building → Approach → Key Decisions → Risks → Verification.
- Same header structure as `/plan` output, but written as a standalone document
  rather than a conversation artifact.

### Postmortem

- Incident summary → Timeline → Root cause → Impact → Fix → Lessons →
  Action items (owner + deadline).
- Blameless tone. Focus on system failures, not individual mistakes.

### Weekly Report (飞书周进展)

Structure: 概述 → 画板 (optional) → 主要进展 → 后续安排.

- 动词开头写"做了什么" — e.g. "完成了 X 的联调", "修复了 Y 的同步问题".
- 主要进展只写已发生的事，用完成时；计划和将来时（"将会/准备/计划"）
  一律归入后续安排.
- 不搞一二三分节 — use natural grouping by topic.
- Keep each progress item to 1-2 sentences.

### KB Knowledge Article

Route to the knowledge-writeback skill declared in `shared/project-routing.md`
(if mounted) — it owns the KB frontmatter contract. This skill provides the
document structure; the KB skill validates the schema. No routing table →
write a plain markdown knowledge note instead.

### Feishu Document

For delivering a local markdown to Feishu, route to:
- `/markdown-to-lark-doc` — whole-file import with mermaid → 画板 conversion.
- `/lark-doc` — direct Feishu document editing.

### Other

For Notion delivery → `/notion-md-sync`.
For a project main doc, route to the main-doc skill declared in
`shared/project-routing.md` (if mounted). No routing table → deliver it as a
regular design doc in local markdown.

## Markdown Conventions

- Mermaid node text wraps with `<br/>`, not `\n`.
- Tables: escape `|` in cell content.
- One blank line before and after fenced code blocks.

## Structure Discipline

- Cross-section repetition: if the same fact appears in two sections, keep it
  in one and reference it from the other.
- Tables do not re-read: do not repeat table data in surrounding prose.
- No vague referents: replace "几个方向 / 一些问题 / 这些东西" with a counted,
  exact category noun — "三类风险", "两个待决项", "六类用途".
- Before deleting a section, confirm the information is captured elsewhere.

## Prose Quality Floor

<!-- Items 4-5 and the no-vague-referents rule distilled from
     Pluviobyte/rnskill (renhua), MIT-spirit idea reuse, no dependency. -->

A mechanical self-scan before delivering any document — zero-judgment checks,
applied to this skill's own output by default, and the full floor when
`/write` is unavailable (e.g. on a work machine without Waza):

1. No em-dash (`—`) — use a comma, period, or parenthetical.
2. Chinese-English boundary: add a space between CJK and Latin characters.
3. Deliver only a finished draft — no "here's a starting point" hedging.
4. Scan for high-frequency AI shells; if found, rewrite the sentence to state
   the claim directly: "不是…而是", "真正 / 本质上", "更重要的是".
5. Verb tense matches work state: completed work in completed form
   ("测了 / 修复了"), future tense only for real next steps.

For deeper polish, route to `/write`.

## Gotchas

| What happened | Rule |
|---|---|
| Wrote a README when asked to "write about X" | Confirm the document type first; default to design doc for technical topics |
| Weekly report had numbered lists 1/2/3 | Use natural topic grouping, not numbered sections |
| KB article missing frontmatter | Route KB knowledge to the writeback skill in `shared/project-routing.md`, which owns the schema |
| Delivered a half-draft with "you can expand this" | Deliver only finished content; if scope is unclear, ask first |

## Output

The document file in markdown, plus:
- Delivery route named (Feishu / Notion / KB / local)
- Any sections that need user input flagged inline
