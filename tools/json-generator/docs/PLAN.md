# JSON生成ツール 公開サイト用JSON出力 実装計画

## Goal

JIS第一・第二水準の漢字、Unihan `kRSUnicode`、部首定義、キュレーション入力から、生成ツール内部の検証用JSONと公開サイトMVPが直接読むサイト用JSONを決定的に出力できる状態にする。

この計画はJSON生成ツール側の実装を扱う。公開サイトUIの外部JSON読込、ロード状態、エラー表示、ブラウザ確認は `docs/PLAN.md` の責務とする。

## Scope Boundary

- 生成ツール側で扱うもの:
  - JIS第一・第二水準の列挙
  - Unihan `kRSUnicode` の読込と康熙部首番号による絞り込み
  - 部首定義の読込
  - キュレーション入力のマージ
  - 生成ツール内部JSONの出力
  - 公開サイト用JSONへの変換
  - JSON構文、参照、重複、相対パスの検証
- 公開サイト側で扱うもの:
  - `data/site-index.json`
  - `data/radicals/*.json`
  - `design/radical-kanji-ui.html` の外部JSON読込実装
  - HTTPサーバー経由のUI動作確認
- この計画では扱わないもの:
  - IDSによる部品検索
  - JIS X 0213第三・第四水準
  - Unicode全文字集合
  - 読み、英語名、説明文の完全自動生成
  - サーバーAPI、DB、CMS、全文検索インデックス

## Directory Ownership

- `tools/json-generator/src/kanji_roman_generator/`
  - Python実装本体を置く。
- `tools/json-generator/scripts/`
  - 手元実行しやすい薄いCLIラッパーを置く。
- `tools/json-generator/config/`
  - 部首定義など、生成ツールの設定を置く。
- `tools/json-generator/curation/`
  - 人手で確認・補足する読み、ローマ字、英語名、説明、部品表示、メモ、タグを置く。
- `tools/json-generator/vendor/`
  - Unihanなど外部由来データのローカル参照先にする。再配布条件を確認できるまで、大きな外部データ本体はコミット対象にしない。
- `tools/json-generator/outputs/`
  - 生成ツール内部JSON、検証ログ、レビュー用中間出力を置く。
- `tools/json-generator/tests/`
  - 生成ロジック、変換、検証の単体テストを置く。
- `data/`
  - ブラウザが直接読む完成品のサイト用JSONのみを置く。生成ツールの設定、キュレーション元データ、vendorデータ、中間出力は置かない。

## Files To Create Or Modify

- Create: `tools/json-generator/src/kanji_roman_generator/__init__.py`
- Create: `tools/json-generator/src/kanji_roman_generator/jis.py`
- Create: `tools/json-generator/src/kanji_roman_generator/unihan.py`
- Create: `tools/json-generator/src/kanji_roman_generator/radicals.py`
- Create: `tools/json-generator/src/kanji_roman_generator/curation.py`
- Create: `tools/json-generator/src/kanji_roman_generator/internal_json.py`
- Create: `tools/json-generator/src/kanji_roman_generator/site_json.py`
- Create: `tools/json-generator/src/kanji_roman_generator/validation.py`
- Create: `tools/json-generator/src/kanji_roman_generator/cli.py`
- Create: `tools/json-generator/scripts/generate_site_json.py`
- Create: `tools/json-generator/config/radicals.json`
- Create: `tools/json-generator/curation/fish.json`
- Create: `tools/json-generator/tests/test_jis.py`
- Create: `tools/json-generator/tests/test_unihan.py`
- Create: `tools/json-generator/tests/test_site_json.py`
- Create: `tools/json-generator/tests/test_validation.py`
- Modify: `docs/radical-kanji-json-tool-design.md`
  - 既存の生成ツール設計を主軸に保ち、公開サイト用JSON出力の入口とディレクトリの責務だけを同期する。
- Generated: `tools/json-generator/outputs/internal/fish.json`
- Generated: `data/site-index.json`
- Generated: `data/radicals/fish.json`

`design/radical-kanji-ui.html` はこの計画では変更しない。UI実装は `docs/PLAN.md` の作業で行う。

## Input Contracts

### Radical Config

`tools/json-generator/config/radicals.json`

```json
[
  {
    "id": "fish",
    "glyph": "魚",
    "labelJa": "魚へん",
    "labelEn": "Fish radical",
    "radical": "魚",
    "displayRadical": "魚",
    "kangxiRadicalNumber": 195,
    "title": "魚へんの漢字",
    "copy": "辞書上の部首が魚に分類されるJIS第一・第二水準の漢字。",
    "tags": ["fish", "seafood", "sushi"],
    "theme": {
      "accent": "#0f766e",
      "accentRgb": "15 118 110",
      "darkAccent": "#5eead4",
      "darkAccentRgb": "94 234 212"
    }
  }
]
```

Validation:

- `id` は英小文字、数字、ハイフンだけを使う。
- `kangxiRadicalNumber` は1から214の整数にする。
- `tags` に `"All"` を入れない。
- `theme` は `data/site-index.json` にそのまま出せる4項目を持つ。

### Curation Input

`tools/json-generator/curation/<id>.json`

```json
{
  "鰆": {
    "name": "Japanese Spanish mackerel",
    "meaning": "A spring-associated fish commonly eaten in Japan.",
    "readings": {
      "ja": ["さわら", "サワラ"],
      "romaji": ["sawara"]
    },
    "parts": {
      "ja": "魚 + 春",
      "en": "Fish + 春 component"
    },
    "note": "Human-facing wording is draft until reviewed against a reliable source.",
    "tags": ["fish", "spring", "food"],
    "curationStatus": "draft",
    "needsReview": true,
    "sourceLabel": "",
    "sourceUrl": "",
    "sourceCheckedAt": "",
    "reviewNote": ""
  }
}
```

Validation:

- 文字キーは1文字の漢字にする。
- `curationStatus` は `reviewed`, `draft`, `unreviewed` のいずれかにする。
- `readings.ja`, `readings.romaji`, `tags` は配列にする。
- `tags` に `"All"` を入れない。
- `sourceLabel`, `sourceUrl`, `sourceCheckedAt`, `reviewNote` は任意の文字列として扱う。
- `reviewed` にする場合は、出典名と確認日を curation input に残す。
- 対象部首のJIS集合に存在しない文字は警告として出す。

### Vendor Input

`tools/json-generator/vendor/Unihan.zip`

- 入力として使うプロパティは `kRSUnicode` に限定する。
- 取得元URL、Unicodeバージョン、取得日、利用条件の確認結果を `tools/json-generator/vendor/README.md` に記録してから利用する。
- 実装とテストは、実データ本体に依存しすぎないよう、小さなテスト用文字列でも `kRSUnicode` 解析を確認できる形にする。

## Output Contracts

### Internal Generator JSON

`tools/json-generator/outputs/internal/<id>.json`

```json
{
  "schemaVersion": "0.1",
  "generatedAt": "2026-06-23T00:00:00+09:00",
  "source": {
    "characterSet": "JIS X 0208 Level 1 and Level 2",
    "jisMethod": "EUC-JP decode from kuten rows 16-84",
    "unihan": {
      "property": "kRSUnicode",
      "sourceFile": "tools/json-generator/vendor/Unihan.zip"
    }
  },
  "group": {
    "id": "fish",
    "glyph": "魚",
    "labelJa": "魚へん",
    "labelEn": "Fish radical",
    "kangxiRadicalNumber": 195
  },
  "items": []
}
```

Internal item fields:

- `char`
- `unicode`
- `codePoint`
- `jis.standard`
- `jis.level`
- `jis.kuten`
- `radical.char`
- `radical.labelJa`
- `radical.labelEn`
- `radical.kangxiRadicalNumber`
- `name`
- `meaning`
- `readings.ja[]`
- `readings.romaji[]`
- `parts.ja`
- `parts.en`
- `note`
- `tags[]`
- `curationStatus`
- `needsReview`
- `sourceLabel`
- `sourceUrl`
- `sourceCheckedAt`
- `reviewNote`

### Public Site Index

`data/site-index.json`

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
        "accent": "#0f766e",
        "accentRgb": "15 118 110",
        "darkAccent": "#5eead4",
        "darkAccentRgb": "94 234 212"
      }
    }
  ]
}
```

Validation:

- `defaultRadical` は `radicals[].id` のいずれかにする。
- `radicals[].file` は `site-index.json` から見た相対パスにする。
- `/data/...` のルート相対パスを出力しない。
- `radicals[].file` が指すファイルは `data/` 配下に存在する。

### Public Radical JSON

`data/radicals/<id>.json`

```json
{
  "schemaVersion": "0.1",
  "id": "fish",
  "glyph": "魚",
  "title": "魚へんの漢字",
  "copy": "辞書上の部首が魚に分類されるJIS第一・第二水準の漢字。",
  "tags": ["fish", "seafood", "sushi", "spring", "food"],
  "items": [
    {
      "char": "鰆",
      "name": "Japanese Spanish mackerel",
      "meaning": "A spring-associated fish commonly eaten in Japan.",
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
      "note": "Human-facing wording is draft until reviewed against a reliable source.",
      "tags": ["fish", "spring", "food"],
      "curationStatus": "draft"
    }
  ]
}
```

Validation:

- `tags` に `"All"` を入れない。
- `items[].unicode` は `items[].char` の実際のコードポイントと一致させる。
- `items[].jis.level` は `1` または `2` にする。
- `items[].curationStatus` は `reviewed`, `draft`, `unreviewed` のいずれかにする。
- `items[]` はJIS区点順を既定にし、同じ入力から同じ順序で出力する。

## Internal To Public Mapping

| Internal | Public | Rule |
|---|---|---|
| `group.id` | `id` | 同じ値を使う |
| `group.glyph` | `glyph` | 部首表示用の字形を使う |
| config `title` | `title` | 部首別JSONの見出しに使う |
| config `copy` | `copy` | 部首別JSONの説明に使う |
| config `tags` + item `tags` | top-level `tags` | 重複を除き、初出順で結合する |
| item `char` | item `char` | 同じ値を使う |
| item `name` | item `name` | キュレーション値を使い、未入力なら空文字にする |
| item `meaning` | item `meaning` | キュレーション値を使い、未入力なら空文字にする |
| item `readings` | item `readings` | 未入力なら空配列にする |
| item `unicode` | item `unicode` | `U+XXXX` 形式で出す |
| item `jis.level` | item `jis.level` | `1` または `2` で出す |
| item `jis.kuten` | item `jis.kuten` | `NN-NN` 形式で出す |
| item `parts` | item `parts` | 未入力なら `ja`, `en` を空文字にする |
| item `note` | item `note` | 未入力なら空文字にする |
| item `tags` | item `tags` | `"All"` を除外し、重複を除く |
| item `curationStatus` | item `curationStatus` | 未入力なら `unreviewed` にする |
| item `needsReview`, `sourceLabel`, `sourceUrl`, `sourceCheckedAt`, `reviewNote` | omitted | generator-side review metadataとして公開JSONには出さない |

## Implementation Phases

### Phase 1: JIS列挙と基礎検証

Files:

- Create: `tools/json-generator/src/kanji_roman_generator/jis.py`
- Create: `tools/json-generator/tests/test_jis.py`

Steps:

1. `enumerate_jis_x0208_kanji()` を実装し、区点16-84区、1-94点をEUC-JP復号で列挙する。
2. 各itemに `char`, `unicode`, `codePoint`, `jis.level`, `jis.kuten` を持たせる。
3. 16-47区は水準1、48-84区は水準2として扱う。
4. テストで `level`、`kuten` 形式、Unicode一致、重複なしを確認する。

Acceptance:

- `PYTHONPATH=tools/json-generator/src python3 -m unittest tools/json-generator/tests/test_jis.py` が成功する。

### Phase 2: Unihan読込と部首フィルタ

Files:

- Create: `tools/json-generator/src/kanji_roman_generator/unihan.py`
- Create: `tools/json-generator/src/kanji_roman_generator/radicals.py`
- Create: `tools/json-generator/tests/test_unihan.py`

Steps:

1. `Unihan.zip` から `Unihan_IRGSources.txt` を優先して読み、`kRSUnicode` 行だけを解析する。古いfixture互換として `Unihan_RadicalStrokeCounts.txt` もfallbackとして扱う。
2. `U+9C06 kRSUnicode 195.9` のような値から先頭の康熙部首番号を抽出する。
3. `tools/json-generator/config/radicals.json` を読み、`kangxiRadicalNumber` と照合して対象文字を絞り込む。
4. 複数値を持つ `kRSUnicode` は、いずれかの値の先頭番号が対象番号と一致すれば対象に含める。

Acceptance:

- 小さなテスト用 `kRSUnicode` 文字列で魚部首と非魚部首を分けられる。
- `PYTHONPATH=tools/json-generator/src python3 -m unittest tools/json-generator/tests/test_unihan.py` が成功する。

### Phase 3: 内部JSON生成

Files:

- Create: `tools/json-generator/src/kanji_roman_generator/internal_json.py`
- Create: `tools/json-generator/src/kanji_roman_generator/cli.py`
- Create: `tools/json-generator/scripts/generate_site_json.py`
- Create: `tools/json-generator/config/radicals.json`
- Generated: `tools/json-generator/outputs/internal/fish.json`

Steps:

1. `generate_internal_group(radical_id)` を実装し、JIS列挙、Unihan部首判定、部首定義を結合する。
2. 出力順は既定でJIS区点順にする。
3. `--radical fish` と `--all` をCLIで選べるようにする。
4. `--sort jis` と `--sort unicode` を受け付ける。
5. `--include-unreviewed` を既定動作にし、`--reviewed-only` はキュレーション対応後に有効化する。
6. `--coverage-report <path>` で生成対象部首ごとの `reviewed`, `draft`, `unreviewed` 件数をJSON出力できるようにする。

Acceptance:

- 次のコマンドで内部JSONが生成される。

```bash
PYTHONPATH=tools/json-generator/src python3 -m kanji_roman_generator.cli \
  --radical fish \
  --radicals tools/json-generator/config/radicals.json \
  --unihan tools/json-generator/vendor/Unihan.zip \
  --curation-dir tools/json-generator/curation \
  --out-dir tools/json-generator/outputs/internal \
  --site-data-dir data \
  --default-radical fish
```

### Phase 4: キュレーションマージ

Files:

- Create: `tools/json-generator/src/kanji_roman_generator/curation.py`
- Create: `tools/json-generator/curation/fish.json`
- Create: `tools/json-generator/tests/test_site_json.py`

Steps:

1. `tools/json-generator/curation/<id>.json` を文字キーで読み込む。
2. JIS/Unihan由来のitemに、`name`, `meaning`, `readings`, `parts`, `note`, `tags`, `curationStatus`, `needsReview`, `sourceLabel`, `sourceUrl`, `sourceCheckedAt`, `reviewNote` をマージする。
3. キュレーションがないitemは `curationStatus: "unreviewed"`、表示文字列は空文字、配列は空配列にする。
4. 対象部首のJIS集合に存在しないキュレーション文字は警告に入れ、生成自体は継続する。
5. `--reviewed-only` は `curationStatus: "reviewed"` のitemだけを公開サイト用JSONへ出す。

Acceptance:

- 手入力した `鰆` のキュレーションが内部JSONと公開サイト用JSONに反映される。
- 範囲外キュレーション文字が警告として検出される。

### Phase 5: 公開サイト用JSON出力

Files:

- Create: `tools/json-generator/src/kanji_roman_generator/site_json.py`
- Generated: `data/site-index.json`
- Generated: `data/radicals/fish.json`

Steps:

1. `site-index.json` を `tools/json-generator/config/radicals.json` から生成する。
2. `radicals[].file` は `radicals/<id>.json` として出力する。
3. 部首別JSONは内部JSONを公開サイト契約へ変換して生成する。
4. 公開JSONから `generatedAt`, `source`, `radical.kangxiRadicalNumber`, `needsReview`, source review fields などの生成ツール内部情報を外す。
5. top-level `tags` は部首定義の `tags` とitemの `tags` を初出順で結合する。

Acceptance:

- `data/site-index.json` から参照される `data/radicals/fish.json` が存在する。
- `data/site-index.json` に `/data/` で始まるパスが出ない。
- 公開JSONの `tags` に `"All"` が出ない。

### Phase 6: 検証と設計書同期

Files:

- Create: `tools/json-generator/src/kanji_roman_generator/validation.py`
- Create: `tools/json-generator/tests/test_validation.py`
- Modify: `docs/radical-kanji-json-tool-design.md`
- Modify: `hooks/validate-project.sh` if the existing hook cannot cover a generated public JSON rule.

Steps:

1. JSON構文、部首定義config、必須キー、重複id、重複char、Unicode一致、JIS水準、`All` タグ混入、相対パスを検証する。
2. `hooks/preflight.sh` でルート `data/` の公開JSONが検証されることを確認する。
3. `docs/radical-kanji-json-tool-design.md` のディレクトリ例とCLI例を `tools/json-generator/` 配下の責務に合わせる。
4. `docs/static-json-site-design.md` は公開サイト側設計書として扱い、この生成ツール計画からは参照に留める。

Acceptance:

- `PYTHONPATH=tools/json-generator/src python3 -m unittest discover -s tools/json-generator/tests` が成功する。
- `bash hooks/preflight.sh` が成功する。
- Markdown内に未整理の作業メモが残っていない。

## Validation Commands

Run these before handoff after implementation:

```bash
PYTHONPATH=tools/json-generator/src python3 -m unittest discover -s tools/json-generator/tests
bash hooks/preflight.sh
! rg -n "/data/" data design tools/json-generator/src tools/json-generator/scripts
```

For UI changes performed under `docs/PLAN.md`, also run a local HTTP server and manually check initial display, radical switching, search, tag filtering, detail card, theme toggle, and failed JSON path behavior.

## Implementation Order

1. Phase 1: JIS列挙と基礎検証
2. Phase 2: Unihan読込と部首フィルタ
3. Phase 3: 内部JSON生成
4. Phase 4: キュレーションマージ
5. Phase 5: 公開サイト用JSON出力
6. Phase 6: 検証と設計書同期

Each phase should leave the repository in a validated state. Public-site UI changes should start only after `data/site-index.json` and at least one `data/radicals/<id>.json` can be generated and pass `hooks/preflight.sh`.
