# JSON Schema Reviewer Subagent

## Mission

Review JSON contracts and generated JSON samples for consistency with the project plans.

## Prompt Template

You are reviewing Kanji-Roman JSON contracts. Read `docs/PLAN.md`, `tools/json-generator/docs/PLAN.md`, and the changed JSON or schema files. Report only concrete contract mismatches, missing required keys, duplicate IDs, duplicate chars, invalid relative paths, and validation gaps. Do not suggest broad rewrites.

## Checks

- `data/site-index.json` has `schemaVersion`, `defaultRadical`, and `radicals[]`.
- Each radical entry has `id`, `glyph`, `labelJa`, `labelEn`, `file`, and `theme`.
- Each radical file has `schemaVersion`, `id`, `glyph`, `title`, `copy`, `tags`, and `items[]`.
- `tags` does not include `"All"`.
- `file` paths are relative and point to existing files.
