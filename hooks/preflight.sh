#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$ROOT/hooks/validate-project.sh"

echo
echo "[kanji-roman] optional local browser check:"
echo "  cd '$ROOT'"
echo "  python3 -m http.server 8000"
echo "  open http://127.0.0.1:8000/"
echo "  open http://127.0.0.1:8000/design/radical-kanji-ui.html"
