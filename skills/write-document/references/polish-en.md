# English AI-Tone Smells

<!-- Distilled from tw93/Waza skills/write/references/write-en.md (MIT), rewritten in own words; no dependency. -->

## How to use

This is a catalog of smells, not a checklist. Recognize the pattern, then decide. A sentence that already reads natural stays, even if it contains a listed word. One trope used once can be fine; the smell is several stacking up or one repeating. Fix by subtraction: cut the performance and state the claim. Do not swap one formula for another ("human" does not mean slangy or quirky), do not invent color to replace what you cut, and keep the author's viewpoint ("I" stays "I"), feelings, hedges, and attributions. Remove emoji from edited prose. Technical wording rules (filler words, AI shells, em dash, vague words) live in `style-en.md` 9.4, 9.8, 8.10, and section 1; this file does not repeat them.

## Word choice

Any word that signals importance instead of saying something is suspect.

- **Emphasis adverbs.** quietly, deeply, fundamentally, remarkably, arguably, genuinely, honestly, literally, actually, really. Cut when they only add weight; keep when they change meaning.
  NO: "quietly orchestrating workflows" / OK: say what it does.
- **Inflated vocabulary.** Prefer the plain word.

| Inflated | Plain |
|---|---|
| utilize, harness | use |
| streamline | simplify, cut |
| navigate (challenges) | handle |
| unpack | explain |
| paradigm | model, approach |
| landscape, ecosystem | field, community |
| tapestry, synergy | mix, combination |
| game-changer | name the actual effect |
| deep dive | analysis |
| moving forward | next, from now on |

- **Pompous copulas.** "serves as", "stands as", "represents", "marks" usually mean "is".
- **Lazy extremes and vague declaratives.** "every", "always", "never", "The reality is simpler", "The reasons are structural". Name the thing and show the evidence before the verdict.

## Sentence structures

Constructions that perform insight instead of delivering it.

- **Negative parallelism** (the most common tell). NO: "It's not bold. It's backwards." / "Not because X, but because Y." / "The question isn't X. It's Y." OK: state Y.
- **Rhetorical self-questions.** NO: "The result? Devastating." OK: "The result was devastating."
- **Anaphora.** NO: "They assume... They assume... They assume..." OK: one sentence, one subject.
- **Stacked tricolons.** NO: three parallel contrasts or three "X didn't build Y" in a row. OK: make the point once with one example.
- **False ranges.** NO: "From innovation to cultural transformation." OK: name the two things, or pick one.
- **Dramatic fragments.** NO: "He published this. Openly. In a book." OK: a complete sentence.
- **False agency.** NO: "The data wants a cleaner narrative." OK: say what the data supports or who decided. "The tool reads the file" is plain technical English and stays.

## Tone patterns

- **Suspense transitions.** NO: "Here's the kicker." / "Here's where it gets interesting." OK: make the point.
- **Decorative analogies.** NO: "Think of it as a Swiss Army knife." Keep an analogy only if the paragraph collapses without it, it survives being pushed one step further, and the reader needs no extra explanation. Otherwise state the idea.
- **Futurist invitation.** NO: "Imagine a world where..." OK: describe what exists or what you propose.
- **Performed vulnerability.** NO: "And yes, I'm openly in love with this model." Real candor is specific; skip the polish.
- **Stakes inflation.** NO: "will define the next era of computing". OK: say what it does.
- **Hand-holding and announcements.** NO: "Let's break this down." / "One detail is easy to miss." OK: start with the content.
- **Vague attribution.** NO: "Experts argue..." / "Reports suggest..." OK: name, link, or quote the source; no source means no claim.
- **Invented concept labels.** NO: "the supervision paradox", "the acceleration trap". OK: describe the thing; do not name it as if it were an established term.
- **Stock morals.** A closing lesson the author never held is a smell; the author's own conviction or heartfelt ending is content and stays.

## Paragraph and composition

- **Bold-first bullets.** NO: every bullet opens with "**Security**:", "**Performance**:". OK: write bullets as sentences or drop the labels.
- **Fractal summaries.** NO: "In this section, we'll explore..." then "As we've seen..." then "In conclusion...". OK: skip preview and recap; end without announcing the end. Exception: one orienting sentence in a TL;DR for non-specialist readers is navigation; flag it at most.
- **Dead metaphor.** One metaphor repeated across the piece. Use it once.
- **One-point dilution.** The same argument restated many ways. Say it once, then add evidence or move on.
- **"Despite these challenges" formula.** Either address the challenges or do not raise them.
- **Meta captions.** NO: "This diagram lists the sensor stack. With it in view, the earlier problems become easier to place." / "I made this with an image model." OK: let the image stand and let the surrounding judgment carry it. Keep creation details only when they are part of the story.
- **Repeated callbacks.** After cutting recaps, do not add a callback to the same project at every section end. A callback earns its place only when it adds a new consequence or limit.
- **Monotone rhythm.** Fragment-heavy or same-length sentences across a paragraph. Repair the rhythm without quotas on sentence length, list size, or paragraph endings.
