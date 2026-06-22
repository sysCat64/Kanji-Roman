#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[kanji-roman] validating project files"

python3 - "$ROOT" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
json_files = [
    path for path in root.rglob("*.json")
    if "node_modules" not in path.parts and ".git" not in path.parts
]

for path in json_files:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        rel = path.relative_to(root)
        raise SystemExit(f"Invalid JSON in {rel}: {exc}") from exc

site_index = root / "data" / "site-index.json"
if site_index.exists():
    data = json.loads(site_index.read_text(encoding="utf-8"))
    required = {"schemaVersion", "defaultRadical", "radicals"}
    missing = sorted(required - set(data))
    if missing:
        raise SystemExit(f"data/site-index.json missing keys: {', '.join(missing)}")

    seen_ids = set()
    for radical in data.get("radicals", []):
        rid = radical.get("id")
        if not rid:
            raise SystemExit("data/site-index.json has radical without id")
        if rid in seen_ids:
            raise SystemExit(f"duplicate radical id: {rid}")
        seen_ids.add(rid)

        file_value = radical.get("file")
        if not file_value:
            raise SystemExit(f"radical {rid} missing file")
        if file_value.startswith("/"):
            raise SystemExit(f"radical {rid} uses root-relative file path: {file_value}")
        target = site_index.parent / file_value
        if not target.exists():
            raise SystemExit(f"radical {rid} file does not exist: {target.relative_to(root)}")

        radical_data = json.loads(target.read_text(encoding="utf-8"))
        if "All" in radical_data.get("tags", []):
            raise SystemExit(f"{target.relative_to(root)} includes forbidden tag 'All'")
        chars = [item.get("char") for item in radical_data.get("items", [])]
        duplicates = sorted({char for char in chars if char and chars.count(char) > 1})
        if duplicates:
            raise SystemExit(f"{target.relative_to(root)} has duplicate chars: {', '.join(duplicates)}")

print(f"Parsed {len(json_files)} JSON file(s)")
PY

if command -v rg >/dev/null 2>&1; then
  if rg -n '/data/' "$ROOT" \
    --glob '*.html' \
    --glob '*.js' \
    --glob '*.css' \
    --glob '*.json' \
    --glob '!node_modules/**' \
    --glob '!.git/**' \
    --glob '!mcp/local-filesystem.template.json'; then
    echo "[kanji-roman] root-relative /data/ path found" >&2
    exit 1
  fi

  placeholder_pattern='(TO''DO:|TB''D:|\[TO''DO|\[TB''D)'
  if rg -n "$placeholder_pattern" "$ROOT" --glob '!node_modules/**' --glob '!.git/**'; then
    echo "[kanji-roman] placeholder marker found" >&2
    exit 1
  fi
else
  echo "[kanji-roman] rg not found; skipped path and placeholder scans"
fi

echo "[kanji-roman] validation passed"
