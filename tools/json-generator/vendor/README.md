# Vendor Data

This directory is the local input area for external data used by the JSON
generator.

## Unihan.zip

- Source URL: https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip
- Unicode version: 17.0.0
- Source date: 2025-08-15
- Checked on: 2026-06-23
- Retrieval status: not committed
- Local filename: `Unihan.zip`
- License: Unicode License v3
- Terms page: https://www.unicode.org/copyright.html
- License text: https://www.unicode.org/license.txt

`Unihan.zip` is required when running
`tools/json-generator/scripts/generate_site_json.py` against real Unihan data.
Keep the archive local unless redistribution has been reviewed for the specific
release.

The generator currently reads `kRSUnicode` from `Unihan_IRGSources.txt`, with
`Unihan_RadicalStrokeCounts.txt` accepted as a legacy fixture fallback.
