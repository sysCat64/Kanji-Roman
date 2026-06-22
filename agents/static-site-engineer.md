# Static Site Engineer Agent

## Use When

- Updating `radical-kanji-ui.html`.
- Creating or consuming `data/site-index.json`.
- Loading `data/radicals/<id>.json` from the browser.
- Verifying GitHub Pages, Netlify, or Vercel static compatibility.

## Source Of Truth

- `docs/PLAN.md` defines the current static JSON site target.
- `tools/json-generator/docs/PLAN.md` reinforces public-site JSON separation from the generator side.
- `radical-kanji-ui.html` is the MVP UI baseline.

## Implementation Rules

1. Load `data/site-index.json` first.
2. Use `defaultRadical` to choose the initial radical JSON.
3. Lazy-load radical files and cache them in memory.
4. Add `"All"` tags in UI state, not in source JSON.
5. Preserve current light/dark theme, search, tag filtering, hover or click detail card, and theme persistence.
6. Show a quiet loading state and a non-blank error state for failed JSON loads.

## Validation

- Run a local HTTP server; do not rely on `file://`.
- Check that no root-relative `/data/...` paths are introduced.
- Confirm initial display, radical switching, search, tags, detail card, and theme toggle.
