# Kanji-Roman

JIS第一・第二水準の漢字を部首別JSONとして整理し、海外の日本語・漢字好き向けに静的HTMLサイトで公開するための設計・試作プロジェクトです。

最初のMVPでは、JIS X 0208の第一・第二水準漢字を対象に、Unicode Unihanの部首情報を使って「魚へん」「糸へん」「草かんむり」「木へん」などのテーマ別データを生成します。読み、ローマ字、英語名、文化的説明、タグなどの人手確認が必要な内容は、機械生成データとは分けてキュレーションJSONとして重ねます。

## Documents

主要な設計と計画は `docs/` と `tools/json-generator/docs/` にあります。

| File | Role |
|---|---|
| `docs/radical-kanji-json-tool-design.md` | JIS列挙、Unihan部首判定、キュレーションマージ、JSON生成CLIの設計書 |
| `docs/PLAN.md` | 静的HTMLと外部JSONへ分離する公開サイトMVPの作成計画 |
| `tools/json-generator/docs/PLAN.md` | 公開サイト用JSON設計書の作成計画と、生成ツール設計への最小追記方針 |

`design/radical-kanji-ui.html` は既存MVP UIの基準です。設計やデータ契約だけを扱う作業では、不用意に変更しません。

## Scope

このプロジェクトでは、生成ツール側と公開サイト側の責務を分けます。

| Area | Responsibility |
|---|---|
| JSON generation tool | JIS第一・第二水準の列挙、Unicodeコードポイント出力、JIS水準と区点の出力、Unihan `kRSUnicode` による部首絞り込み、キュレーションJSONのマージ、出力検証 |
| Static public site | `data/site-index.json` と `data/radicals/*.json` を読み込み、部首ナビ、検索、タグ絞り込み、詳細カード、テーマ切替をクライアント側で表示 |

MVPの部首分類は、見た目の位置ではなく辞書上の部首に基づきます。たとえば「漁」は構成要素として魚を含みますが、部首は水なので「魚へん」のMVPデータには含めません。構成要素検索は将来のIDS連携で扱う拡張です。

## Data Generation Design

生成ツールは、JIS X 0208の漢字領域をEUC-JPの区点から列挙します。

- 第一水準: 16区から47区
- 第二水準: 48区から84区
- 対象文字数: 6,355字

部首判定にはUnicode Unihanの `kRSUnicode` を使い、康熙部首番号で対象グループを絞り込みます。部首定義は `fish`, `thread`, `grass`, `tree` などの安定したIDを持ち、表示名として「魚へん」「糸へん」「草かんむり」「木へん」などを使います。

生成されるitemには、次のような情報を含めます。

- `char`
- `unicode`
- `codePoint`
- `jis.level`
- `jis.kuten`
- `radical`
- `readings`
- `meanings`
- `components`
- `componentPhrase`
- `notes`
- `tags`
- `curationStatus`

機械生成で確定できるJIS、Unicode、部首情報と、人手確認が必要な読み、英語名、文化メモ、タグは分離します。再生成しても手作業のキュレーションが失われない構造にします。

## Static Site JSON Contract

公開サイトMVPは、サーバーAPIやDBを使わない静的構成です。UIは最初に `data/site-index.json` を読み込み、部首ナビと初期表示対象を決めます。

`data/site-index.json` の主なフィールド:

- `schemaVersion`
- `defaultRadical`
- `radicals[]`
- `radicals[].id`
- `radicals[].glyph`
- `radicals[].labelJa`
- `radicals[].labelEn`
- `radicals[].file`
- `radicals[].theme`

部首別JSONは `data/radicals/<id>.json` に配置します。`site-index.json` 内の `file` は、`site-index.json` から見た相対パスにします。

部首別JSONの主なフィールド:

- `schemaVersion`
- `id`
- `glyph`
- `title`
- `copy`
- `tags`
- `items[]`

`tags` には `"All"` を含めません。UI側がタグ一覧の先頭に `"All"` を追加します。

`items[]` の主なフィールド:

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

公開サイトで使うJSON取得パスは、GitHub Pagesのサブパス公開でも壊れにくい相対パスにします。ローカルファイルを直接開く動作は対応前提にせず、確認はHTTPサーバー経由で行います。

## UI Behavior

公開サイトMVPでは、既存UIの次の挙動を維持します。

- ライトテーマとダークテーマの切替
- 部首ナビの切替
- 検索
- タグ絞り込み
- ホバーまたはクリックによる詳細カード表示
- JSON読み込み中のloading表示
- JSON読み込み失敗時のエラー表示

テーマ設定のみ `localStorage` に保存します。JSONデータはブラウザストレージに保存しません。

## Local Preview

ローカル確認はHTTPサーバー経由で行います。

```bash
python3 -m http.server 8000
```

既存MVP UIを確認する場合は、ブラウザで次を開きます。

```text
http://localhost:8000/design/radical-kanji-ui.html
```

静的公開用JSON分離への移行後は、初期表示、部首切替、検索、タグ、詳細カード、テーマ切替を確認します。

## Validation

設計と実装の確認では、次を重視します。

- Markdownの本文が確定した表現になっていること
- JSONが存在する場合は全件パースできること
- `site-index.json` から参照される部首別JSONファイルが存在すること
- `char` と `unicode` が一致すること
- JIS区点と `char` が重複しないこと
- `jis.level` が1または2であること
- 部首番号がグループ定義と一致すること
- キュレーション対象の文字がJIS第一・第二水準に含まれること
- 公開サイト用のパスが相対パスとして扱われること

## Data Sources And Licensing

生成ツールは、JIS X 0208の列挙、Unicode Unihan、将来拡張としてCJKVI IDSの利用を想定します。Unihan、IDS、辞書説明文、フォントなど外部由来データを使う場合は、ライセンスと再配布条件を確認します。

英語名や文化的説明は揺れが出やすいため、`needsReview` や `curationStatus` を使って確認状態を明示します。Unicodeコードポイントは符号位置であり、表示字体はフォントに依存します。
