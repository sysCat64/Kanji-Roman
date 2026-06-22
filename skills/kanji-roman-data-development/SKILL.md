---
name: kanji-roman-data-development
description: Use when working on the Kanji-Roman project, especially radical kanji JSON generation, static HTML plus external JSON migration, curation data, validation hooks, or reviews of docs/PLAN.md, tools/json-generator/docs/PLAN.md, docs/radical-kanji-json-tool-design.md, radical-kanji-ui.html, or data/*.json files.
---

# Kanji-Roman Data Development

## Overview

Use this skill to keep Kanji-Roman work aligned with the current generator design and static-site JSON split.

## Start Here

1. Read `docs/PLAN.md` for the current static publishing target and `tools/json-generator/docs/PLAN.md` for generator-side public JSON output planning.
2. Read `docs/radical-kanji-json-tool-design.md` before touching generator behavior or data contracts.
3. Use `radical-kanji-ui.html` as the MVP UI baseline.
4. For detailed contracts and checks, read `references/project-contracts.md` and `references/review-checklist.md`.

## Work Routing

- Generator work: JIS enumeration, Unihan parsing, radical filtering, curation merge, deterministic output.
- Static-site work: `data/site-index.json`, `data/radicals/<id>.json`, browser fetch paths, loading and error states.
- Curation work: readings, romaji, English meanings, notes, tags, `needsReview`, and `curationStatus`.
- Review work: contract mismatches, root-relative paths, missing validation, source and license risk.

## Hard Rules

- Keep generator output contracts and public-site JSON contracts distinct.
- Use relative JSON paths such as `data/site-index.json` and `radicals/fish.json`.
- Do not rely on `file://`; verify browser behavior through a local HTTP server.
- Add `"All"` in UI state only. Do not store it in radical JSON `tags`.
- Preserve manual curation across regeneration.
- Mark uncertain human-facing content as draft or needs-review.

## Validation

Run `hooks/preflight.sh` before handoff when hook scripts are present. If code or UI changed, also perform the relevant manual browser checks from `references/review-checklist.md`.
