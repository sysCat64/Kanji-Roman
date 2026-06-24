# 静的公開対応 JSON 分離サイト 実装計画

## Goal

既存の `design/radical-kanji-ui.html` を、インラインの `collections` データに依存する試作UIから、ルートの `data/site-index.json` と `data/radicals/*.json` をHTTP経由で読む静的公開MVPへ移行する。

この計画は公開サイト側だけを扱う。JIS列挙、Unihan読込、部首フィルタ、キュレーションマージ、生成CLIは `tools/json-generator/docs/PLAN.md` の責務とする。

## Architecture

公開サイトはビルドツールなしの静的HTMLとして維持する。`design/radical-kanji-ui.html` からは `../data/site-index.json` を読み、部首ナビを生成し、`defaultRadical` が指す部首JSONを遅延取得する。

移行中は既存HTML内の `collections` を公開JSONフィクスチャへ写す。生成ツールが完成した後は、同じ公開JSON契約で `data/` を再生成できる状態にする。

## Tech Stack

- Static HTML, CSS, vanilla JavaScript
- Browser `fetch()`
- Browser `localStorage` for theme only
- Local HTTP verification with `python3 -m http.server`
- Existing repo validation through `hooks/preflight.sh`

---

## Scope Boundary

- 公開サイト側で扱うもの:
  - `docs/static-json-site-design.md`
  - `design/radical-kanji-ui.html`
  - `data/site-index.json`
  - `data/radicals/fish.json`
  - `data/radicals/grass.json`
  - `data/radicals/tree.json`
  - `data/radicals/thread.json`
- 公開サイト側で扱わないもの:
  - JIS第一・第二水準の列挙
  - Unihan `kRSUnicode` の解析
  - 部首定義からの生成
  - キュレーション入力のマージ
  - `tools/json-generator/` 配下の実装
  - サーバーAPI、DB、CMS、全文検索インデックス

## Files To Create Or Modify

- Create: `docs/static-json-site-design.md`
  - 公開サイトのJSON契約、読込フロー、UI状態、失敗時表示、検証方法を記録する。
- Create: `data/site-index.json`
  - 起動時に読む部首インデックスを置く。
- Create: `data/radicals/fish.json`
  - 既存UIの魚へんデータを公開JSON契約へ移す。
- Create: `data/radicals/grass.json`
  - 既存UIの草かんむりデータを公開JSON契約へ移す。
- Create: `data/radicals/tree.json`
  - 既存UIの木へんデータを公開JSON契約へ移す。
- Create: `data/radicals/thread.json`
  - 既存UIの糸へんデータを公開JSON契約へ移す。
- Modify: `design/radical-kanji-ui.html`
  - インライン `collections` を削除し、外部JSON読込、メモリキャッシュ、ロード表示、エラー表示へ置き換える。
- Modify: `hooks/validate-project.sh` only if the current hook cannot validate a public-site rule required by this plan.

## Public JSON Contract

### `data/site-index.json`

```json
{
  "schemaVersion": "0.1",
  "defaultRadical": "fish",
  "radicals": [
    {
      "id": "fish",
      "glyph": "魚",
      "labelJa": "魚へん",
      "labelEn": "Fish radical",
      "file": "radicals/fish.json",
      "theme": {
        "accent": "#5f8f98",
        "accentRgb": "95 143 152",
        "darkAccent": "#86b1b8",
        "darkAccentRgb": "134 177 184"
      }
    }
  ]
}
```

Rules:

- `defaultRadical` must match one `radicals[].id`.
- `radicals[].file` is relative to `data/site-index.json`.
- Use `radicals/fish.json`, not a root-relative path.
- `theme` contains `accent`, `accentRgb`, `darkAccent`, and `darkAccentRgb`.
- Because the current HTML is under `design/`, the UI fetches the index with `../data/site-index.json`; `radicals[].file` still remains relative to the loaded index.

### `data/radicals/<id>.json`

```json
{
  "schemaVersion": "0.1",
  "id": "fish",
  "glyph": "魚",
  "title": "Fish Radical Collection",
  "copy": "Kanji shaped by sea, seasons, food culture, and old naming habits.",
  "tags": ["Season", "Sushi", "Nature", "Everyday", "Poetic"],
  "items": [
    {
      "char": "鰆",
      "name": "Sawara",
      "meaning": "Japanese Spanish mackerel",
      "readings": {
        "ja": ["さわら", "サワラ"],
        "romaji": ["sawara"]
      },
      "unicode": "U+9C06",
      "jis": {
        "level": 2,
        "kuten": "82-54"
      },
      "parts": {
        "ja": "魚 + 春",
        "en": "Fish + 春 component"
      },
      "note": "In Japan, sawara is often associated with spring and seasonal cooking.",
      "tags": ["Season", "Sushi", "Poetic"],
      "curationStatus": "draft"
    }
  ]
}
```

Rules:

- Top-level `tags` does not contain `"All"`; the UI adds `"All"` at render time.
- `items[].tags` does not contain `"All"`.
- `items[].unicode` matches `items[].char`.
- `items[].jis.level` is `1` or `2`.
- `items[].curationStatus` is `reviewed`, `draft`, or `unreviewed`.
- Initial fixture data may keep existing human-facing wording from `design/radical-kanji-ui.html`; uncertain wording stays `draft`.

## Existing UI Mapping

| Current Inline Field | Public JSON Field | Rule |
|---|---|---|
| `collections.<id>.glyph` | radical `glyph` | Same value |
| `collections.<id>.title` | radical `title` | Same value |
| `collections.<id>.copy` | radical `copy` | Same value |
| `collections.<id>.accent` | site-index `theme.accent` | Same value |
| `collections.<id>.accentRgb` | site-index `theme.accentRgb` | Convert comma format to space-separated RGB |
| `collections.<id>.darkAccent` | site-index `theme.darkAccent` | Same value |
| `collections.<id>.darkAccentRgb` | site-index `theme.darkAccentRgb` | Convert comma format to space-separated RGB |
| `collections.<id>.tags` | radical `tags` | Remove `"All"` |
| item `reading` | item `readings.ja` and `readings.romaji` | Kana values go to `ja`; romanized value goes to `romaji` |
| item `jis` | item `jis.level` and `jis.kuten` | Parse `Level N / NN-NN` |
| item `partsJa` | item `parts.ja` | Same value |
| item `partsEn` | item `parts.en` | Same value |
| item other fields | matching item fields | Same value |
| no current field | item `curationStatus` | Use `draft` for migrated human-facing copy |

## Runtime State

- `state.radical`: current radical id.
- `state.tag`: current tag; initial value is `"All"`.
- `state.search`: current search text.
- `state.selectedChar`: current selected character or empty string before data is loaded.
- `state.theme`: `"light"` or `"dark"` from `localStorage`.
- `state.siteIndex`: loaded `site-index.json`.
- `state.collections`: object cache keyed by radical id.
- `state.loading`: boolean for quiet loading display.
- `state.error`: user-facing error message or empty string.

Only `state.theme` is persisted to `localStorage`. JSON data is kept in memory only.

## Implementation Phases

### Phase 1: Public JSON Fixtures

Files:

- Create: `data/site-index.json`
- Create: `data/radicals/fish.json`
- Create: `data/radicals/grass.json`
- Create: `data/radicals/tree.json`
- Create: `data/radicals/thread.json`

Steps:

1. Create `data/site-index.json` with four radicals: `fish`, `grass`, `tree`, and `thread`.
2. Set `defaultRadical` to `fish`.
3. Set each `radicals[].file` to `radicals/<id>.json`.
4. Move each existing inline collection into its matching `data/radicals/<id>.json`.
5. Remove `"All"` from every radical JSON `tags` array.
6. Convert item `reading` arrays into `readings.ja` and `readings.romaji`.
7. Convert item `jis` strings into `{ "level": N, "kuten": "NN-NN" }`.
8. Convert `partsJa` and `partsEn` into `parts.ja` and `parts.en`.
9. Set migrated item `curationStatus` to `draft`.

Acceptance:

- `bash hooks/preflight.sh` parses all JSON files and reports validation passed.
- `data/site-index.json` references all four radical JSON files.
- No public JSON file contains `"All"` in stored `tags`.

### Phase 2: Static Site Design Doc

Files:

- Create: `docs/static-json-site-design.md`

Steps:

1. Document the public JSON contracts from this plan.
2. Document the startup flow: load site index, build radical navigation, load default radical, render.
3. Document the radical switching flow: reuse cached data or fetch the radical JSON by relative file path.
4. Document loading and error UI states.
5. Document that `file://` is unsupported and local preview uses `python3 -m http.server`.
6. Document that `"All"` is UI state only and is not stored in radical JSON.

Acceptance:

- `docs/static-json-site-design.md` points generator internals back to `tools/json-generator/docs/PLAN.md`.
- The design doc does not introduce root-relative JSON paths.

### Phase 3: External JSON Loading In UI

Files:

- Modify: `design/radical-kanji-ui.html`

Steps:

1. Replace the inline `collections` object with `state.siteIndex` and `state.collections`.
2. Add `loadSiteIndex()` using `fetch("../data/site-index.json")`.
3. Add `resolveRadicalUrl(file)` using `new URL(file, new URL("../data/site-index.json", window.location.href))`.
4. Add `loadRadical(radicalId)` that finds the radical entry, fetches its file, caches it, and returns normalized render data.
5. Add `normalizeRadical(indexEntry, radicalData)` so existing rendering code can consume `glyph`, `title`, `copy`, `theme`, `tags`, and `items`.
6. Add `"All"` to the rendered tag list in `renderTags()` without mutating loaded JSON.
7. Update `matchesSearch()`, `setSelected()`, and card rendering to use `readings`, `jis.level`, `jis.kuten`, and `parts`.
8. Initialize through an async `init()` function instead of `setSelected(collections.fish.items[0])`.

Acceptance:

- Initial load reads root `data/site-index.json` through `../data/site-index.json` from `design/radical-kanji-ui.html`.
- The default radical loads from `defaultRadical`.
- Existing search, tags, detail card, and theme toggle continue to work.
- No JSON data is stored in `localStorage`.

### Phase 4: Loading And Error States

Files:

- Modify: `design/radical-kanji-ui.html`

Steps:

1. Add a quiet loading state in the grid area while the site index or radical JSON is being fetched.
2. Add an error state in the grid area if the first load fails.
3. Keep the previously displayed radical visible if a later radical switch fails.
4. Keep the detail panel closed or unchanged when the current data set is unavailable.
5. Use concise user-facing text; do not expose stack traces, local paths, or implementation details.

Acceptance:

- A missing initial `data/site-index.json` shows a readable error instead of a blank UI.
- A missing radical JSON after initial load leaves the previous radical usable.
- The error state can be manually verified by temporarily changing one `file` value in `data/site-index.json`.

### Phase 5: Dynamic Radical Navigation

Files:

- Modify: `design/radical-kanji-ui.html`

Steps:

1. Generate `.radical-tab` buttons from `siteIndex.radicals`.
2. Use each entry's `id`, `glyph`, `labelJa`, `labelEn`, and `theme.accent`.
3. Preserve the existing visual style of the sidebar buttons.
4. On click, clear search text, reset tag to `"All"`, load the selected radical, and render.
5. Update `aria-pressed` based on `state.radical`.

Acceptance:

- Adding a new radical entry to `data/site-index.json` and a matching radical JSON file adds a sidebar button without editing HTML markup.
- Radical switching lazy-loads uncached JSON and reuses cached JSON on later visits.

### Phase 6: Validation And Manual Browser Check

Files:

- Modify: `hooks/validate-project.sh` only if needed.

Steps:

1. Run `bash hooks/preflight.sh`.
2. Confirm root-relative public data paths are absent from HTML, JS, CSS, and JSON.
3. Start a local HTTP server with `python3 -m http.server 8000`.
4. Open `http://127.0.0.1:8000/design/radical-kanji-ui.html`.
5. Check initial display.
6. Check radical switching.
7. Check search.
8. Check tag filtering.
9. Check detail card selection.
10. Check theme toggle persistence.
11. Check failed radical JSON behavior by temporarily changing one `file` value in `data/site-index.json`, then restore it.

Acceptance:

- `bash hooks/preflight.sh` reports validation passed.
- Manual browser checks pass over HTTP.
- The repo has no temporary broken JSON path left after the failed-path check.

## Validation Commands

Run these before handoff after implementation:

```bash
bash hooks/preflight.sh
! rg -n "/data/" data design --glob "*.html" --glob "*.js" --glob "*.css" --glob "*.json"
python3 -m http.server 8000
```

Open:

```text
http://127.0.0.1:8000/design/radical-kanji-ui.html
```

Manual checks:

- Initial display
- Radical switching
- Search
- Tag filtering
- Detail card
- Theme toggle
- Failed radical JSON path behavior

## Implementation Order

1. Phase 1: Public JSON Fixtures
2. Phase 2: Static Site Design Doc
3. Phase 3: External JSON Loading In UI
4. Phase 4: Loading And Error States
5. Phase 5: Dynamic Radical Navigation
6. Phase 6: Validation And Manual Browser Check

Each phase should leave the repository in a state where `bash hooks/preflight.sh` passes. UI behavior must be verified over HTTP, not by opening the HTML through `file://`.
