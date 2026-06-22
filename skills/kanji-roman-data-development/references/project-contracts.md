# Project Contracts

## Public Site Index

`data/site-index.json`:

- `schemaVersion`
- `defaultRadical`
- `radicals[]`
- `radicals[].id`
- `radicals[].glyph`
- `radicals[].labelJa`
- `radicals[].labelEn`
- `radicals[].file`
- `radicals[].theme`
- `radicals[].theme.accent`
- `radicals[].theme.accentRgb`
- `radicals[].theme.darkAccent`
- `radicals[].theme.darkAccentRgb`

`radicals[].file` is relative to `data/site-index.json`, for example `radicals/fish.json`.

## Public Radical File

`data/radicals/<id>.json`:

- `schemaVersion`
- `id`
- `glyph`
- `title`
- `copy`
- `tags`
- `items[]`

`tags` excludes `"All"` because the UI adds it.

## Public Radical Item

`items[]`:

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

`curationStatus` is `reviewed`, `draft`, or `unreviewed`.

## Generator Contract

The generator uses JIS X 0208 first and second level kanji, Unihan `kRSUnicode`, radical definitions, and optional curation JSON. It should output deterministic JSON and report curation entries outside the target set.

