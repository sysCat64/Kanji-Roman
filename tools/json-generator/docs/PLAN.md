# 静的公開対応 JSON 設計書 作成計画

## Summary
公開サイトMVP用の設計書を新規作成し、既存の `radical-kanji-json-tool-design.md` には最小限の追記だけ行う。生成ツール設計と公開サイト設計を分け、責務が混ざらない構成にする。

## Key Changes
- 新規作成: `radical-kanji-static-site-design.md`
  - 静的ホスティング前提、外部JSON読込、UIデータ契約、失敗時表示、ローカル確認方法を定義する。
- 追記: `radical-kanji-json-tool-design.md`
  - 「公開サイト用JSON出力」セクションを追加し、生成ツールが将来 `site-index.json` と部首別サイト用JSONを出せることを明記する。
- 既存UI `radical-kanji-ui.html` は、設計書内でMVP表示仕様の基準として参照するだけで、この設計書作成ステップでは変更しない。

## Directory Layout
- この計画はJSON生成ツール側の設計・実装配置を扱う。
- 生成ツール側の主な対象:
  - `tools/json-generator/docs/`
  - `tools/json-generator/src/`
  - `tools/json-generator/config/`
  - `tools/json-generator/curation/`
  - `tools/json-generator/vendor/`
  - `tools/json-generator/outputs/`
- `tools/json-generator/config/` は部首定義などの生成設定を置く。
- `tools/json-generator/curation/` は手作業で確認・補足する読み、ローマ字、英語名、メモ、タグなどの入力元を置く。
- `tools/json-generator/vendor/` はUnihanやIDSなど外部由来データのローカル参照先として扱い、ライセンスと再配布条件を確認してから追加する。
- `tools/json-generator/outputs/` は生成確認用の中間出力や検証対象を置く。
- 公開サイト用JSONを生成するときの最終出力先は、ルートの `data/site-index.json` と `data/radicals/*.json` とする。
- ルートの `data/` には、生成ツールの設定、キュレーション元データ、vendorデータ、一時出力を置かない。
- 公開サイトUIの実装と挙動確認は `docs/PLAN.md` 側の責務とする。

## Public Interfaces
- `data/site-index.json`
  - `schemaVersion`
  - `defaultRadical`
  - `radicals[]`: `id`, `glyph`, `labelJa`, `labelEn`, `file`, `theme`
  - `theme`: `accent`, `accentRgb`, `darkAccent`, `darkAccentRgb`
- `data/radicals/<id>.json`
  - `schemaVersion`, `id`, `glyph`, `title`, `copy`, `tags`, `items[]`
  - `tags` には `"All"` を含めず、UI側で追加する。
- `file` は `site-index.json` からの相対パスにする。
  - 例: `"radicals/fish.json"`
  - `/data/...` のようなルート相対パスは GitHub Pages のサブパス公開で壊れやすいので禁止する。

## Test Cases
- Markdown確認
  - 新規設計書と既存設計書に `TODO`, `TBD`, 未決定の仮置き表現が残っていないことを確認する。
- 仕様整合
  - `radical-kanji-static-site-design.md` のJSON契約が、既存UIの表示項目と対応していることを確認する。
- 公開互換
  - 設計書内のJSON取得パスが相対パスのみで説明されていることを確認する。
- 既存設計との分離
  - 既存設計書は生成ツール仕様を主軸のまま維持し、公開サイト詳細は新規設計書へ誘導する。

## Assumptions
- 公開サイトMVPは Vercel / Netlify / GitHub Pages のどれでも動く静的サイトを前提にする。
- `file://` 直開きは非対応とし、ローカル確認は `python3 -m http.server` などのHTTPサーバー経由にする。
- JSON生成ツールの詳細仕様は既存の `radical-kanji-json-tool-design.md` を正とする。
- 公開UI用JSONは、生成ツールの内部出力そのものではなく、UIが読みやすい軽量な「サイト用JSON」とする。
