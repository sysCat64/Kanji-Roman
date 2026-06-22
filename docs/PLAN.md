# 静的公開対応 JSON 分離サイト設計書 作成計画

## Summary
`docs/static-json-site-design.md` を新規作成し、現在の `radical-kanji-ui.html` を将来の Vercel / Netlify / GitHub Pages 公開に耐える「静的HTML + 外部JSON」構成へ移行するための仕様書にする。対象は「公開サイトMVP」で、データ生成CLIの詳細は既存の `radical-kanji-json-tool-design.md` に委ねる。

## Key Changes
- 公開サイトはサーバーAPIなしの静的構成にする。
- JSONはUIが直接読みやすい「サイト用JSON」を採用する。
- すべてのJSONパスは `data/...` の相対パスにし、GitHub Pages のサブパス公開でも壊れない前提にする。
- `file://` 直開きは非対応と明記し、ローカル確認は `python3 -m http.server` などのHTTPサーバー経由にする。
- 既存のライト/ダークテーマ、検索、タグ、ホバー/クリック詳細カードのUI挙動は維持する。

## Directory Ownership
- この計画は公開サイトMVP側の構成とデータ契約を扱う。
- 公開サイト側の主な対象:
  - `docs/static-json-site-design.md`
  - `design/radical-kanji-ui.html`
  - `data/site-index.json`
  - `data/radicals/*.json`
- ルートの `data/` は、ブラウザが直接読む完成品のサイト用JSON置き場として扱う。
- 生成ツールのCLI、設定、キュレーション元データ、外部vendorデータ、一時出力は `tools/json-generator/` 側の責務とし、この計画では内部実装を扱わない。
- 公開サイトは生成ツールが出力したサイト用JSONを消費するが、生成ツール内部の中間形式には依存しない。

## Public Interfaces
- `data/site-index.json`
  - `schemaVersion`
  - `defaultRadical`
  - `radicals[]`: `id`, `glyph`, `labelJa`, `labelEn`, `file`, `theme`
  - `theme`: `accent`, `accentRgb`, `darkAccent`, `darkAccentRgb`
- `data/radicals/<id>.json`
  - `schemaVersion`, `id`, `glyph`, `title`, `copy`, `tags`, `items[]`
  - `tags` は `"All"` を含めない。UIが先頭に `"All"` を追加する。
- `items[]`
  - `char`, `name`, `meaning`
  - `readings`: `ja[]`, `romaji[]`
  - `unicode`
  - `jis`: `level`, `kuten`
  - `parts`: `ja`, `en`
  - `note`
  - `tags[]`
  - `curationStatus`: `reviewed | draft | unreviewed`

## Implementation Guidance To Capture In The Design Doc
- 起動時に `data/site-index.json` を読み、部首ナビを動的生成する。
- 初期表示は `defaultRadical` の `file` を読み込む。
- 部首クリック時は対象JSONを遅延読み込みし、読み込み済みデータはメモリキャッシュする。
- JSON読み込み中は一覧領域に静かな loading 表示を出す。
- JSON読み込み失敗時はエラー表示を出し、既に表示済みの部首があればそれを残す。
- 検索・タグ絞り込み・詳細カード表示は、読み込まれた部首データに対してクライアント側で行う。
- テーマ設定のみ `localStorage` に保存し、JSONデータは保存しない。

## Test Plan
- JSON構文確認: `node -e` で `data/site-index.json` と `data/radicals/*.json` を全件 `JSON.parse` する。
- スキーマ確認: 必須キー、重複 `id`、重複 `char`、タグ参照、`file` パス存在を検証する。
- ローカルHTTP確認: `python3 -m http.server 8000` で開き、初期表示、部首切替、検索、タグ、詳細カード、テーマ切替を確認する。
- 公開互換確認: `/data/...` のようなルート相対パスが残っていないことを検索で確認する。
- 失敗系確認: 存在しないJSONパスにした場合、UIが白紙化せずエラー状態を表示することを確認する。

## Assumptions
- 設計書の作成先は `docs/static-json-site-design.md` とする。
- 現在の `radical-kanji-ui.html` はMVPのUI基準として扱う。
- 既存の `radical-kanji-json-tool-design.md` はデータ生成ツール側の設計書として残し、新設計書から参照する。
- MVPではビルドツール、DB、サーバーAPI、全文検索インデックス、CMS連携は扱わない。
- 公開サイトに同梱するフォントは、再配布ライセンスが明確なものだけを使う。
