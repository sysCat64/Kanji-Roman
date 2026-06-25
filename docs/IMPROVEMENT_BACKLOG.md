# Improvement Backlog

## Purpose

This document tracks post-MVP improvement work for Kanji-Roman after the static
JSON site and JSON generator are usable.

Keep the project split clear:

- Public-site UI work belongs with `docs/PLAN.md`, `design/radical-kanji-ui.html`,
  and `data/`.
- Generator and data-production work belongs with
  `tools/json-generator/docs/PLAN.md`, `tools/json-generator/src/`,
  `tools/json-generator/config/`, and `tools/json-generator/curation/`.
- Finished public JSON in `data/` should be regenerated from generator inputs
  when the change starts from kanji data, readings, tags, or curation text.

## Current Baseline

- The public site reads `data/site-index.json` and `data/radicals/*.json` over
  HTTP.
- GitHub Pages deployment is handled by `.github/workflows/pages.yml`.
- The UI supports radical switching, search, tag filtering, detail cards,
  loading states, error states, and theme persistence.
- The generator can produce internal JSON and public-site JSON from JIS,
  Unihan `kRSUnicode`, radical config, and curation input.
- `hooks/preflight.sh` is the main repository validation gate.

## Curation Workflow

Use this workflow when adding readings, romaji, English names, meanings, parts,
notes, or tags for individual kanji.

1. Pick a radical id and character from generated data.
   - Public output lives in `data/radicals/<id>.json`.
   - Curation source input lives in `tools/json-generator/curation/<id>.json`.
2. Edit the curation input, not the generated public JSON first.
   - Use the kanji character as the object key.
   - Keep machine-derived fields such as Unicode, JIS level, and kuten under
     generator control.
3. Fill curation fields conservatively.
   - `name`: short display name in English.
   - `meaning`: concise reader-facing meaning or gloss.
   - `readings.ja`: kana readings, including common kana variants when useful.
   - `readings.romaji`: romanized readings in a consistent project style.
   - `parts.ja` and `parts.en`: readable visual component phrase for the UI,
     not a claim about etymology or literal meaning.
     - Default to glyph-based labels: `parts.ja` uses forms such as
       `魚 + 里`, and `parts.en` keeps the right-side glyph with `component`,
       such as `Fish + 里 component`.
     - Use an English gloss only as a reviewed, deliberate reader-facing
       exception, not as a broad automatic conversion from kanji to English
       meanings.
     - Leave `parts` blank for standalone characters or when the breakdown
       would require stroke-level or overly obscure pieces.
   - `note`: short cultural or usage note only when wording has been reviewed.
   - `tags`: small topical tags used by the UI.
   - `curationStatus`: use `draft` while wording needs review; use `reviewed`
     only after checking a reliable source.
   - `needsReview`: keep `true` until the entry has been checked.
   - `sourceLabel`, `sourceUrl`, `sourceCheckedAt`, and `reviewNote`:
     generator-side review metadata for entries that have source checks.
4. Regenerate internal and public JSON with the generator CLI after curation
   changes.
5. Review generator warnings, especially curation entries that do not appear in
   the generated radical item set.
6. Run validation:

```bash
PYTHONPATH=tools/json-generator/src python3 -m unittest discover -s tools/json-generator/tests
bash hooks/preflight.sh
```

7. Preview over HTTP and check the changed radical:

```bash
python3 -m http.server 8000
```

Open `http://127.0.0.1:8000/design/radical-kanji-ui.html`.

## Near-Term Backlog

### Curation Sources And Provenance

Reviewed readings, names, meanings, and notes record source checks in
generator-side curation input. Public JSON does not expose source metadata; a UI
display for sources belongs in a separate public-site change.

Supported curation input fields:

- `sourceLabel`: human-readable source name.
- `sourceUrl`: source URL when a stable URL is available.
- `sourceCheckedAt`: source check date in `YYYY-MM-DD` form.
- `reviewNote`: short internal note describing what was checked.

### Fish Radical Curation Baseline

The first `fish` editorial pass is complete enough to serve as the reference
workflow for other radicals. The public `data/radicals/fish.json` output has 73
items marked `reviewed`; the standalone `魚` entry intentionally leaves
`parts.ja` and `parts.en` blank.

Keep future fish changes small and source-checked:

1. Adjust individual readings, names, meanings, notes, or tags only after
   reviewing a reliable source.
2. Keep `parts` wording glyph-based unless a deliberate reader-facing exception
   is reviewed.
3. Regenerate `tools/json-generator/outputs/internal/fish.json` and
   `data/radicals/fish.json`.

### Curation Files For Other Radicals

The `grass` curation file has started with a small source-checked seed batch.
Create curation files for `tree` and `thread` when editorial work starts for
those radicals. Keep each PR scoped to one radical or one curation theme so
generated diffs stay reviewable.

### Curation Coverage Report Baseline

The generator CLI can write a curation coverage report with
`--coverage-report <path>`. The report counts `reviewed`, `draft`, and
`unreviewed` entries per generated radical while leaving internal and public
JSON output unchanged.

Current coverage:

- `fish`: 73 total, 73 reviewed, 0 draft, 0 unreviewed.
- `grass`: 278 total, 30 reviewed, 0 draft, 248 unreviewed.
- `tree`: 356 total, 0 reviewed, 0 draft, 356 unreviewed.
- `thread`: 173 total, 0 reviewed, 0 draft, 173 unreviewed.

### Reviewed-Only Output Baseline

The `--reviewed-only` flow has been exercised against the current generator and
curation inputs. It filters public radical JSON items to reviewed entries while
keeping internal output complete.

Current public reviewed-only counts:

- `fish`: 73 items.
- `grass`: 30 items.
- `thread`: 0 items.
- `tree`: 0 items.

Keep the default public site on the normal output until the other initial
radicals have reviewed curation. Use `--reviewed-only` for curated showcase
builds or focused checks where empty non-fish radical pages are acceptable.

## UI Improvement Backlog

### Keyboard And Focus

Review keyboard navigation for radical tabs, tag chips, kanji cards, the detail
panel, and the theme toggle. Keep the visual style calm and consistent with the
current Taisho and Showa-retro direction.

### Mobile Detail Panel

Check long kanji details on small screens. Improve panel spacing and close
behavior if longer readings or notes make the card feel crowded.

### Search Feedback

Search already checks characters, names, meanings, readings, parts, notes,
status text, and tags. After more readings are curated, review whether result
counts and empty states still feel clear.

### Public Release Review

Before treating the site as a stable public MVP, run the manual HTTP or Pages
check against:

- Initial load
- Radical switching
- Search
- Tag filtering
- Detail card
- Theme persistence
- Failed radical JSON recovery

## Later Backlog

### IDS Component Search

Add IDS-based component search as a separate layer from radical search. This is
where characters such as `漁`, which contain `魚` visually but do not use the
fish radical, should eventually belong.

### Additional Radicals

Add new radicals only after the generator and curation flow is comfortable for
the first four radicals. Each new radical needs config, generated output,
validation, and at least a light UI check.

### Static Search Index

Consider a generated search index only if browser-side filtering over the
current radical JSON becomes too slow or if cross-radical search becomes part of
the public UI.

### Release Notes

Add a lightweight release note or changelog process once public data changes
become meaningful to readers, especially when reviewed curation increases.
