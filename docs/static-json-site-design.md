# Static JSON Site Design

## Scope

This document covers the static public site JSON contract and browser loading flow for `design/radical-kanji-ui.html`.

Generator internals such as JIS enumeration, Unihan `kRSUnicode` parsing, curation merge, internal JSON, and CLI generation are owned by `tools/json-generator/docs/PLAN.md`.

## Public JSON Files

The browser reads only files under `data/`:

- `data/site-index.json`
- `data/radicals/<id>.json`

Generator configuration, curation input, vendor data, and internal outputs stay under `tools/json-generator/`.

## Site Index Contract

`data/site-index.json` contains:

- `schemaVersion`
- `defaultRadical`
- `radicals[]`

Each `radicals[]` entry contains:

- `id`
- `glyph`
- `labelJa`
- `labelEn`
- `file`
- `theme.accent`
- `theme.accentRgb`
- `theme.darkAccent`
- `theme.darkAccentRgb`

`radicals[].file` is relative to `data/site-index.json`, for example `radicals/fish.json`. It must not start with a leading slash.

## Radical JSON Contract

`data/radicals/<id>.json` contains:

- `schemaVersion`
- `id`
- `glyph`
- `title`
- `copy`
- `tags[]`
- `items[]`

Each `items[]` entry contains:

- `char`
- `name`
- `meaning`
- `readings.ja[]`
- `readings.romaji[]`
- `unicode`
- `jis.level`
- `jis.kuten`
- `parts.ja`
- `parts.en`
- `note`
- `tags[]`
- `curationStatus`

The public JSON does not expose generator-only fields such as `generatedAt`, `source`, `radical.kangxiRadicalNumber`, or `needsReview`.

## Browser Loading Flow

1. Fetch `../data/site-index.json` from `design/radical-kanji-ui.html`.
2. Build radical navigation from `siteIndex.radicals`.
3. Load `siteIndex.defaultRadical`.
4. Resolve each radical file relative to the loaded index location.
5. Cache loaded radical JSON in memory by radical id.
6. Re-render when the radical, tag, search text, selected item, or theme changes.

Local preview uses an HTTP server, for example:

```bash
python3 -m http.server 8000
```

Direct `file://` opening is not a supported preview mode.

## UI State

The browser keeps:

- current radical id
- current tag
- search text
- selected character
- theme from `localStorage`
- loaded site index
- radical JSON cache
- loading flag
- user-facing error message

Only the theme is persisted. JSON data stays in memory.

## Loading And Errors

The UI should show a quiet loading state while fetching JSON. If the index or a radical JSON file cannot be loaded or parsed, the UI should show a readable error state instead of a blank screen.

## Tags

`"All"` is a UI state only. It must not be stored in `data/site-index.json`, top-level radical `tags`, or item `tags`.

## Validation

The repository validation hook checks public JSON syntax, site-index references, duplicate ids, duplicate item characters, Unicode consistency, JIS level values, forbidden `"All"` tags, and relative file paths.

Run:

```bash
bash hooks/preflight.sh
```
