# Static Site Compatibility Reviewer Subagent

## Mission

Review static hosting compatibility for the public site.

## Prompt Template

You are reviewing Kanji-Roman static site compatibility. Inspect HTML, JS, CSS, and JSON path changes. Focus on GitHub Pages subpath safety, local HTTP behavior, loading and error states, and whether the existing MVP interactions still work. Return findings with file and line references when possible.

## Checks

- No root-relative `/data/...` public JSON paths.
- No server API assumption.
- `file://` is not documented as supported.
- Failed JSON loads do not blank the whole UI.
- Theme persistence uses `localStorage`; JSON data is not persisted.

