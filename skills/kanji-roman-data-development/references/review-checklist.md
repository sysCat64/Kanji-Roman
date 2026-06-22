# Review Checklist

## Docs

- No `TODO` or `TBD` placeholders unless the file is explicitly a future task list.
- Static site documentation uses relative `data/...` paths.
- Generator documentation remains separate from public site JSON details.

## JSON

- All JSON parses successfully.
- `site-index.json` references existing radical files.
- Radical IDs are unique.
- Radical item `char` values are unique within a file.
- `tags` does not include `"All"`.
- `unicode` matches `char` when present.
- `jis.level` is `1` or `2`.

## UI

- Initial load reads `data/site-index.json`.
- The default radical loads from `defaultRadical`.
- Switching radicals lazy-loads data and reuses in-memory cache.
- Search and tag filtering operate on the loaded radical data.
- Loading state is visible but quiet.
- Error state keeps the UI usable.
- Theme is saved in `localStorage`; JSON data is not.

## Manual Browser Checks

Run a local HTTP server and check:

- Initial display.
- Radical switching.
- Search.
- Tag filtering.
- Detail card.
- Theme toggle.
- Failed JSON path behavior.

