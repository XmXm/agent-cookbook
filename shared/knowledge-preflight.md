# Knowledge Preflight Contract

Before starting substantive work at the node listed below, run the two
preflight checks. Both are non-blocking: if a source is unavailable, state
that explicitly and proceed.

## Sources

1. **nmem** — personal decisions, prior art, preferences:
   `nmem --json m search "<topic keywords>"`
2. **Project KB** — domain patterns, cases, postmortems: only when a project
   layer is mounted at `shared/project-routing.md`, search the knowledge
   source it declares, the way it declares it. The routing file may declare
   a Scope section; if the current workspace or task falls outside that
   scope, treat the file as not mounted. No routing table, or out of scope
   → skip this source.

## Nodes (when to preflight)

| Skill | Node |
|---|---|
| plan | Before Design / Refactor mode drafts a recommendation |
| check | Before opening a review (pull relevant anti-patterns for the subsystem) |
| hunt | Before forming hypotheses (search symptoms, similar cases, bug history) |
| write-document | Before drafting (search for document-type conventions, prior examples) |

## Degradation

- No `shared/project-routing.md` mounted, or its KB unreachable → say so,
  skip the project KB preflight, continue.
- `nmem` unavailable → skip nmem preflight, continue.
- Never block the main workflow on a preflight failure.
