# JSON Generator Engineer Agent

## Use When

- Implementing or reviewing scripts that enumerate JIS X 0208 kanji.
- Parsing Unihan `kRSUnicode`.
- Producing radical-group JSON or public-site JSON.
- Validating deterministic output and curation merges.

## Source Of Truth

- Primary: `docs/radical-kanji-json-tool-design.md`
- Static-site contract: `docs/PLAN.md`
- Public JSON split: `tools/json-generator/docs/PLAN.md`

## Implementation Rules

1. Generate JIS first and second level kanji by EUC-JP kuten decoding.
2. Filter MVP radical groups by Kangxi radical number from Unihan `kRSUnicode`.
3. Keep machine-generated fields separate from hand-curated fields.
4. Sort output deterministically, preferably by JIS kuten unless a plan says otherwise.
5. Report curation entries whose `char` is outside the target JIS set.

## Review Checklist

- `unicode` matches the actual code point.
- `jis.level` is `1` or `2`.
- `jis.kuten` is unique.
- `char` is unique within each radical output.
- Public JSON paths are relative to `data/site-index.json`.
