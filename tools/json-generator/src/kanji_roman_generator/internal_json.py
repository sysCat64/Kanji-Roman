from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from kanji_roman_generator.jis import enumerate_jis_x0208_kanji
from kanji_roman_generator.radicals import (
    filter_jis_items_by_radical_id,
    find_radical_definition,
)

SCHEMA_VERSION = "0.1"
CHARACTER_SET = "JIS X 0208 Level 1 and Level 2"
JIS_METHOD = "EUC-JP decode from kuten rows 16-84"
UNIHAN_PROPERTY = "kRSUnicode"


def generate_internal_group(
    radical_id: str,
    radical_definitions: Sequence[Mapping[str, Any]],
    radical_numbers_by_char: Mapping[str, Sequence[int]],
    *,
    jis_items: Sequence[Mapping[str, Any]] | None = None,
    sort_order: str = "jis",
    generated_at: str | None = None,
    unihan_source_file: str = "tools/json-generator/vendor/Unihan.zip",
) -> dict[str, Any]:
    """Generate one internal radical group from JIS, Unihan, and config data."""
    radical = find_radical_definition(radical_definitions, radical_id)
    kangxi_radical_number = int(radical["kangxiRadicalNumber"])
    source_items = (
        list(jis_items)
        if jis_items is not None
        else enumerate_jis_x0208_kanji()
    )
    filtered_items = filter_jis_items_by_radical_id(
        source_items,
        radical_numbers_by_char,
        radical_definitions,
        radical_id,
    )
    sorted_items = _sort_items(filtered_items, sort_order)

    return {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": generated_at or _generated_at_now(),
        "source": {
            "characterSet": CHARACTER_SET,
            "jisMethod": JIS_METHOD,
            "unihan": {
                "property": UNIHAN_PROPERTY,
                "sourceFile": unihan_source_file,
            },
        },
        "group": {
            "id": str(radical["id"]),
            "glyph": _glyph(radical),
            "labelJa": str(radical["labelJa"]),
            "labelEn": str(radical["labelEn"]),
            "kangxiRadicalNumber": kangxi_radical_number,
        },
        "items": [
            _internal_item(item, radical, kangxi_radical_number)
            for item in sorted_items
        ],
    }


def write_internal_group(path: str | Path, group: Mapping[str, Any]) -> None:
    """Write an internal group JSON file with deterministic formatting."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(group, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _internal_item(
    item: Mapping[str, Any],
    radical: Mapping[str, Any],
    kangxi_radical_number: int,
) -> dict[str, Any]:
    return {
        "char": item["char"],
        "unicode": item["unicode"],
        "codePoint": item["codePoint"],
        "jis": dict(item["jis"]),
        "radical": {
            "char": str(radical.get("radical") or _glyph(radical)),
            "labelJa": str(radical["labelJa"]),
            "labelEn": str(radical["labelEn"]),
            "kangxiRadicalNumber": kangxi_radical_number,
        },
        "name": "",
        "meaning": "",
        "readings": {
            "ja": [],
            "romaji": [],
        },
        "parts": {
            "ja": "",
            "en": "",
        },
        "note": "",
        "tags": [],
        "curationStatus": "unreviewed",
        "needsReview": False,
    }


def _sort_items(
    items: Sequence[Mapping[str, Any]],
    sort_order: str,
) -> list[Mapping[str, Any]]:
    if sort_order == "jis":
        return sorted(items, key=lambda item: str(item["jis"]["kuten"]))
    if sort_order == "unicode":
        return sorted(items, key=lambda item: int(str(item["codePoint"]), 16))
    raise ValueError(f"unsupported sort order: {sort_order}")


def _glyph(radical: Mapping[str, Any]) -> str:
    return str(
        radical.get("glyph")
        or radical.get("displayRadical")
        or radical["radical"]
    )


def _generated_at_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
