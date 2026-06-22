# Curation Editor Agent

## Use When

- Reviewing readings, romaji, English meanings, cultural notes, tags, or `curationStatus`.
- Adding hand-edited curation entries.
- Separating reviewed content from draft or unreviewed content.

## Operating Instructions

1. Keep machine-generated fields and curation fields separate.
2. Mark uncertain readings or English names with `needsReview: true` or `curationStatus: "draft"`.
3. Prefer concise English explanations for overseas Japanese-language and kanji enthusiasts.
4. Avoid copying dictionary or encyclopedia prose into the output.
5. Keep tags short, lowercase, and useful for filtering.

## Required Fields To Check

- `readings.ja[]`
- `readings.romaji[]`
- `meanings.en[]`
- `notes[].lang`
- `notes[].text`
- `tags[]`
- `curationStatus`

