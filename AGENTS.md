# Kanji-Roman Agent Guide

## Project Context

- このプロジェクトは、JIS第一・第二水準の漢字を部首別JSONとして生成し、静的HTMLサイトで公開するための設計・試作を扱う。
- `docs/radical-kanji-json-tool-design.md` はJSON生成ツール側の設計書として扱う。
- `docs/PLAN.md` は静的公開対応JSON分離サイトの直近計画として扱う。
- `tools/json-generator/docs/PLAN.md` はJSON生成ツール側から公開サイト用JSON出力を扱う計画として扱う。
- `radical-kanji-ui.html` は既存MVP UIの基準として参照する。設計・データ契約作業だけのときは不用意に変更しない。

## Development Guardrails

- 生成ツール設計と公開サイト設計を混ぜない。CLI、Unihan、JIS列挙、キュレーションマージは生成ツール側。`data/site-index.json` と `data/radicals/*.json` は公開サイト側。
- 静的公開では `data/...` の相対パスを使う。`/data/...` のルート相対パスは GitHub Pages のサブパス公開で壊れやすいので避ける。
- `file://` 直開きは対応前提にしない。ローカル確認はHTTPサーバー経由にする。
- JSONデータは決定的な順序で出力し、再生成しても手作業のキュレーションが失われない構造にする。
- 外部由来データ、辞書説明文、フォント、IDS/Unihanなどはライセンスと再配布条件を確認する。

## Expected Validation

- Markdownに `TODO`、`TBD`、未決定の仮置き表現が残っていないか確認する。
- JSONが存在する場合は全件パースし、`site-index.json` から参照される `file` が存在するか確認する。
- 静的公開互換として、公開サイト用ファイルに `/data/` が残っていないか確認する。
- UI変更を行った場合は、初期表示、部首切替、検索、タグ、詳細カード、テーマ切替をHTTPサーバーで確認する。
