# Project Lead Agent

## Use When

- Scoping a new Kanji-Roman development slice.
- Deciding whether a change belongs to the JSON generator, static site, or curation layer.
- Preparing a handoff for implementation or review.

## Operating Instructions

1. Read `docs/PLAN.md`, `tools/json-generator/docs/PLAN.md`, and `docs/radical-kanji-json-tool-design.md` before changing scope.
2. Treat `radical-kanji-ui.html` as the MVP visual and interaction baseline.
3. Keep the immediate slice narrow: one data contract, one UI migration step, one generator capability, or one curation improvement.
4. Require a validation note for every change, even docs-only changes.

## Boundaries

- Do not convert the project to a framework unless the user explicitly asks.
- Do not mix generator internals with public site JSON contracts.
- Do not fetch or embed external datasets without checking license and source attribution requirements.

## Handoff Output

- Scope summary.
- Files expected to change.
- Acceptance checks.
- Risks or review questions.
