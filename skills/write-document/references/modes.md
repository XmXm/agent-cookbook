# Special Modes

<!-- Distilled from tw93/Waza skills/write (MIT), rewritten in own words; no dependency. -->

Load a section only when the ask matches its triggers. Default work is a line-level edit under SKILL.md Hard Rules; these modes add rules for specific surfaces, they do not relax the Hard Rules. Before returning produced copy in any mode, run `scripts/check.py`.

## Release Notes / Changelog

**Triggers**: release notes, changelog, version notes, update feed, appcast; 发版说明、更新日志、版本说明、写 release。

**Do**:
- Read the target project's release convention (agent instructions, contributing docs) and its most recent published release (changelog, release page, registry page, or `gh release view --json body -R <owner>/<repo>` for GitHub projects). Match its format, tone, sentence length, and density. Its item count is history, not a quota.
- Freeze the artifact boundary first: the last published release and the exact candidate users will receive. A commit after the candidate is not material for it.
- Build the inventory from `git log <last-published>..<candidate>`, not memory. Read every feat and fix commit; small items in commit form can be large for users.
- For each change, name the reader, what differs before and after, and whether the reader sees it or must act. Drop delivery, refactor, CI, registry, observability, and internal API detail unless it changes a visible outcome or requires action. Keep deliberate omissions in working notes, not in the published text.
- Use the smallest set of distinct user outcomes. Merge changes serving the same goal; never split one outcome or pad with internals to match the last release.
- Group by product surface or user-visible verb (Faster startup, Fixed crash on launch), never by "Polish", "Misc", "Chores", or 细节打磨.
- One sentence per item naming the visible change, not the implementation. NO: "Use a queue observer for store updates." OK: "Store updates now run inside the app." Keep a technical term only if readers use it to recognize, configure, or act.
- Without a project style: Breaking Changes, New Features, Fixes and Improvements, Deprecations; numbered items with a bold label and one sentence of user effect. Always call out breaking changes and deprecations.
- No termination signals (final release, 停止维护) unless true. Title: version plus the core change, ten words or fewer. No emoji.
- Release notes and a social announcement are two artifacts. The announcement follows Tweet / Social Post.
- Bilingual only when the project already ships bilingual notes; see Bilingual and Localization Copy for layout. Settle source-language items, order, and labels before translating.
- Every locale keeps the same item count and order but uses native register instead of mirroring source syntax. Chinese blocks use full-width punctuation, English blocks ASCII.
- For HTML-capable update feeds, separate language blocks with headings so the rendered update window does not run them together.

## Public Issue or PR Reply

**Triggers**: reply to issue, reply to PR, comment on #N, close this issue; 回复 issue、回 issue、回 PR、写个评论。

**Do**:
- Re-read the live thread (`gh issue view <num>` or `gh pr view <num>`) before drafting. Titles, states, and reporter languages change.
- Default to one paragraph of one or two sentences. Open with `@<reporter>` and at most one short thanks. Match the reporter's language. No exclamation marks, no stacked courtesy endings (Thanks again, 再次感谢).
- State exactly one ship state: shipped in vX.Y.Z, fixed on the default branch for the next release, available in a preview channel, planned, duplicate, not planned (one-line reason plus an alternative), or needs specific evidence.
- Give one concrete next step: the release to install, the upgrade command, a cache to clear, or exactly what info is missing. The step must work with the reported failure or accessibility need still present.
- Every sentence must be true now: no "shipped" without release evidence this turn, no "landed" while uncommitted, no implied verification that did not happen.
- Root cause only when it changes what the reporter does. Internal symbols, file names, CI, and maintainer process belong in the commit.
- Two short paragraphs only when a one-line command or real ambiguity needs room. No bullets, headers, or code blocks beyond that one command.
- Closing as completed: the comment alone explains what was fixed, the channel, and the expected release. Closing as not planned: the current boundary and an alternative path. Do not lean on earlier thread context.
- Paying users: acknowledge the relationship and the inconvenience in one phrase, then state the boundary and the safest practical path without arguing.
- Ask only for minimum public facts; route logs, dumps, and private state to a private support channel if the project has one.
- Batches: N threads get N replies. Read drafts side by side; if three or more share the opening clause, order, and closing move, rewrite. Each opening comes from that thread's own report.
- Private channels (DM, support email): drop the report register; short colloquial sentences that lead with what the user gets.
- No meta narration about your own process (I re-read and changed this, 前面回复有误). Edit your comment in place only while nobody has replied after it; otherwise post a new one.

**Output**: the final reply text only. If you posted it, read back the body, author, target, and thread state; the action is not done until the readback matches.

## Tweet / Social Post

**Triggers**: tweet, thread, X post, social post, launch post, announcement; 推特、推文、X 推文、长文推特、发文、折叠长度。

**Do**:
- Derive the length budget from the physical constraint (fold line, character limit) or the user's previously accepted posts before writing.
- Lead with a social anchor (who reported it, thanks to users, a milestone) when the project already speaks that way; the change list follows.
- Pick two to four highlights, not the full changelog. Skipping a whole module is fine.
- Frame from the user's side (what it feels like to use), not "this tool does X".
- Include one stance sentence explaining why a decision was made, taken from the author's material.
- Native rhythm: idiomatic phrasing in the post's language; in Chinese avoid translation tone and formal words (具体判据、主轴、本意).
- Close with a casual invitation, not a hard call to action ("give it a try" over "Upgrade now").
- Ground every claim in the shipping artifact per SKILL.md Hard Rules. In a project without that community voice, keep the structure in the project's own voice.

## Long-Form Structural Work

**Triggers**: a long article that needs structural review, cross-section repetition, too long, restructure; 长文结构、结构调整、长文精简、删重复。Several headings or images alone do not trigger this mode.

**Do**:
- Map first, read-only: list every H2 section, table, list, and image. Flag cross-section repetition (the same checklist, judgment, or core claim in two or more sections), table re-reading (prose that walks the rows of the table above it), and whole redundant paragraphs or sections.
- Test each paragraph's contribution. Experience, emotion, conviction, qualifications, and explanation all carry weight; lacking a new fact is not grounds to cut. A shorter, more neutral draft can be worse. Never set a target fraction to delete.
- Respect scope. Read-only asks get proposed change-points. An explicit rewrite authorizes sentence cuts without re-asking; name whole-paragraph cuts in the summary, and ask before deleting a section or reordering headings unless structure was requested.
- Only then de-AI line by line, section by section, with `polish-en.md` or `polish-zh.md`. For language mirrors, check meaning and native rhythm.
- When two sections make the same point, keep the strongest supported version and cut or merge the others; propose the merge as a change-point, not a silent edit.
- After cutting recaps, do not re-anchor every section ending to the same project; a callback stays only if it adds a new consequence or limit.
- Never rewrite a long piece in one pass; it overwrites hand-tuned phrasing and cannot be reviewed as a diff.
- For repository edits, keep frontmatter, code, media, and links, and run the site build if one exists. Do not alter technical examples to satisfy a style rule.

**Output**: a structural map with change-points first; then the edited text or scoped diff, with every whole-paragraph cut listed with its reason.

## Bilingual and Localization Copy

**Triggers**: EN/CN pair, translation review, mixed Chinese/English copy, localization copy, i18n copy, string catalog, multi-locale site; 中英对照、双语、翻译校对、本地化文案、多语言文案。

**Do**:
- Confirm which version is the original. Compare by meaning per paragraph, not line or word counts. Check the translation for added experiences, swapped books or tools, lost uncertainty, "I did" turned into "you should", or an extra moral after a concrete example. Unclear originals get marked for confirmation.
- Each version must read natively on its own: no Chinese comma-chained sentences carried into English, no facts added for rhythm. Keep the author's own stories and recommendations rather than localizing them away.
- One term, one form across the document. Flag untranslated English inside Chinese that has a stable equivalent. Quote direction and pairing need human judgment.
- Bilingual layout: English block first, Chinese block second, as parallel sections; numbered items match one to one; product and feature names identical; never mix languages inside one item.
- Multi-surface products: split surfaces first (feed, site, runtime catalog, help, legal); do not force each to mirror the broadest locale set. Edit source files (templates, locale JSON, catalogs), not generated output, then rebuild and inspect the rendered surface (buttons, menus, notifications, wrapping, glyphs).
- Keep versions, dates, links, shortcuts, identifiers, and placeholders (`%@`, `%1$@`, `{name}`) exact, in order and type. One full sentence per locale; never glue translated fragments.
- The source language is not factual authority. Verify behavior claims against the shipping artifact; recheck quantifiers and causal words (all, only, always, because) in every locale. Do not invent policy to smooth a sentence or polish into generic marketing.
- High-signal failures: Chinese literal possessives (你的 Mac where Mac or 本机 suffices) and machine verbs (检测到); Traditional Chinese with mainland phrasing; Japanese manual-voice UI; German, Spanish, French, Italian ASCII fallbacks and missing accents, plus invalid forms from broad find-and-replace.
- Surface voice defects in any locale: parenthetical padding in titles and labels, hedged verdicts on computed results, implementation nouns (buffer, daemon, quota) as labels, and error strings that report mechanism instead of the reader's next action.
- Patch only intended fields; do not reserialize whole catalogs. Follow broad replacements with residual scans. Track a reading ledger by content ID, locale, and surface; keyword scans and truncated reads do not prove coverage.
- Structural checks are not editorial authority. Compare stable anchors and meaning, not translated line counts or heading positions; a useful addition is not a missing-content failure. If a gate demands deleting correct material, investigate the gate.
- Calibrate automated checkers on one known defect and one normal example before batch edits. A clean result proves only the rules the checker covers, not natural voice or factual accuracy.
- Treat command examples in copy as inert text: keep their bytes intact, never execute them to verify behavior, and localize only field templates meant for readers.
- Reread titles, descriptions, FAQs, alts, and captions against the corrected body so metadata does not restore a removed claim. Inspect images themselves; a correct caption cannot fix a wrong diagram label.

**Output**: rewrites return the localized copy. Reviews group findings by surface, then locale; mark as blockers any copy that misstates behavior, privacy, legal terms, version history, or update availability. Report reading coverage, rendered checks, and untested layers separately.

## Document Review

**Triggers**: review this document, check this document, PDF, white paper; 审稿、文档 review、帮我看看这篇文档。

**Do**:
- Privacy: flag sensitive information not authorized for the intended audience. Identity and experience the author supplied or already published stay; employer names or job seeking alone are not grounds to delete.
- Tone: flag voice shifts, register mismatches, and formulaic phrasing.
- Bilingual pairs: apply Bilingual and Localization Copy.
- Rendering: leftover placeholders (Lorem ipsum, TODO, TBD) and broken images or links.
- Snapshot documents (review reports, scorecards, diagnostics): flag dated claims, stale line references, private paths, repo-specific commands, and current-score framing; recommend extracting stable rules instead of keeping the snapshot as evergreen guidance.

**Output**: the requested review or rewrite; mention privacy only when an actionable concern remains.

## Paragraph Coherence

**Triggers**: coherence, flow check, paragraphs feel disconnected; 连贯性、段落连贯、可读性、段落顺不顺。

**Do**:
- Check unsignalled topic shifts, openings that do not follow the previous paragraph's close, and monotone sentence length within a paragraph.
- Each fix is minimal: one word, one reordered clause, or one bridging sentence.
- Do not reorder paragraphs or add transition stock phrases (Furthermore, 此外, 值得一提的是) to fake flow; a real bridge names the link between the two ideas.

**Output**: review asks get a numbered list keyed by paragraph location. Explicit rewrite or file-edit asks get the minimal edits directly, without asking again.
