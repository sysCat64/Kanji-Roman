#!/usr/bin/env bash
set -euo pipefail

SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="${1:-$SCRIPT_ROOT}"

echo "[kanji-roman] validating project files"

PYTHONPATH="$SCRIPT_ROOT/tools/json-generator/src${PYTHONPATH:+:$PYTHONPATH}" \
  python3 -m kanji_roman_generator.validation "$ROOT"

if command -v rg >/dev/null 2>&1; then
  if rg -n '(^|[^.])/data/' "$ROOT" \
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
