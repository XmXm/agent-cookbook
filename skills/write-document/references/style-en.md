# Technical Wording Rules (English)

<!-- Rules extracted from hai-stack skills/hai-simplified-technical (CC BY-NC 4.0),
     itself based on ASD-STE100 Part 1. Rewritten in own words; no dependency.
     Personal use. Rule numbers are shared with style-zh.md. -->

Goal: the reader can take only one meaning. The rules control wording, not content: keep every fact, condition, exception, and doubt of the source.

How to use:

- Technical text only (see SKILL.md, Scope of the Rule Sets). Persuasive or personal text gets the polish pass only.
- Keep every hard rule. Keep about 80% of the soft rules; break one when it would make the sentence awkward or lose information, and be able to say why.
- Project glossary and style guide win over these rules (chapter 10).
- Rules marked "script" are reported by `scripts/check.py`. A hit is a place to read, not a verdict.
- This is not controlled English: keep natural tenses, phrasal verbs such as "sign in", and domain vocabulary when they carry the right meaning.

## 1 Words

- **1.1 One word per concept (hard).** Do not vary words for style. If "workspace" and "project" name one object, use one.
- **1.2 One meaning per word (hard).** Once "build" means type-check plus bundle, the bundling step alone is "bundle".
- **1.3 Use the glossary (hard).** Name a new concept before you use it.
- **1.4 No vague words (hard, script).** appropriate, relevant, various, significant, substantial, fairly, quite, somewhat, basically, essentially. Give a number, a name, or a condition. When rewriting without the number, drop only the empty intensifier ("improved significantly" → "improved") and list the missing data for the author.
- **1.5 Verbs that say what happens (soft).** handle, process, manage, optimize: say the actual action within the same clause.

## 2 Noun Phrases

- **2.1 At most two modifiers before a noun (soft).**
- **2.2 At most three nouns in a row (soft).** "worker task cancellation policy" hides who cancels what; restore the relation. Glossary terms count as one noun.
- **2.3 Hyphenate a compound modifier before a noun (hard).** "a read-only replica".

## 3 Verbs

- **3.1 Do not hide the verb in a noun (hard, script).** perform, carry out, conduct, make an adjustment. "Perform a validation of the input" → "Validate the input."
- **3.2 Active voice; name the actor (soft).** Passive stays when the actor is unknown or irrelevant. Never invent an actor to make a sentence active.
- **3.3 State facts in the simple tense (soft).** "The scheduler watches the queue", not "is watching".
- **3.4 Fixed requirement words (hard, script).** must / must not (requirement), should / should not (recommendation), can / need not (permission), or the project's RFC 2119 words. Not "need to", "have to", "make sure", "try to", "ideally". Keep the source's strength: "You should inspect the report" does not become "Inspect the report".
- **3.5 A one-word verb when one exists (soft).** "find", not "find out".

## 4 Sentences

- **4.1 One topic per sentence (hard).**
- **4.2 Name the actor (hard).** No empty "It is" or "There is"; no dangling modifiers.
- **4.3 Each pronoun points to one thing (hard).** No bare "this"; if "it" has two candidates, repeat the name.
- **4.4 Show the connection (soft).** because, so, if, but.
- **4.5 Vertical list for three or more parallel items (soft).**
- **4.6 Keep articles and "that" (hard).** No telegraph style.

## 5 Procedures

- **5.1 Numbered list, one instruction per step (hard).**
- **5.2 Start each step with an imperative verb (hard).**
- **5.3 Condition before instruction (hard).** "If X, do Y." Keep necessary vs sufficient: "Restart only if validation passes" is not "If validation passes, restart."
- **5.4 Step sentences at most 20 words (soft).**
- **5.5 Reasons before the list; each result after its step (soft).**

## 6 Descriptive Writing

- **6.1 Conclusion first in each paragraph (hard).**
- **6.2 One topic per paragraph, at most six sentences (soft).**
- **6.3 Descriptive sentences at most 25 words (soft).**
- **6.4 Every measured number has its conditions and date (hard).**
- **6.5 Keep done apart from planned (hard).** Also keep started, queued, and completed distinct.

## 7 Warnings

- **7.1 A warning comes before the step it governs (hard).**
- **7.2 Instruction first, then the risk (hard).** "Do not force-push a shared branch. It overwrites remote history."
- **7.3 One risk per warning (soft).**
- **7.4 Two levels (hard).** **Warning:** data loss, irreversible, silently wrong, production impact, external publishing. **Caution:** slower, rework, long wait.

## 8 Punctuation, Numbers, Length

- **8.1 ASCII punctuation (hard).**
- **8.2 One quotation style per document (hard).**
- **8.3 A space between number and unit (hard).** "30 s", "4 GB"; no space before %.
- **8.6 Ranges with "–" or "to", never "~" (hard, script).**
- **8.7 Dates that cannot be misread (hard).** ISO 8601 in tables and parentheses.
- **8.8 Count words between spaces; a code span counts as one (hard).**
- **8.10 No em dash (hard, script).** Use a comma, period, colon, or parentheses. An en dash inside a numeric range is fine.

## 9 Writing Practices

- **9.1 One form per term (hard).** One spelling and one case.
- **9.2 Code names in backticks, exactly as in code (hard).**
- **9.3 Official product names; define abbreviations at first use (hard).**
- **9.4 No filler or marketing words (soft, script).** simply, just, easily, obviously, seamless, leverage, robust, powerful, out of the box.
- **9.7 No contractions; no e.g., i.e., etc., via (soft).**
- **9.8 No AI shells (soft, script).** "It is worth noting", "delve", "at its core", "not just X but Y". State the claim. More patterns in `polish-en.md`.

## 10 Glossary

Before writing, look for the project glossary: files named glossary or terms, a terms section in `STYLE.md` or `CONTRIBUTING.md`, naming conventions in `AGENTS.md`, `CLAUDE.md`, or the README. Follow it; it wins over these rules. If none exists, pick one word per concept (prefer the code name and the most common existing wording) and hand the small table to the author in the "For the author" note.
