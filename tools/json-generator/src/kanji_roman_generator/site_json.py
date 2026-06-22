from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = "0.1"


def site_index_from_radical_definitions(
    radical_definitions: list[Mapping[str, Any]],
    *,
    default_radical: str | None = None,
) -> dict[str, Any]:
    """Build the public site index from generated radical definitions."""
    if not radical_definitions:
        raise ValueError("site index requires at least one radical definition")

    radical_ids = [str(radical["id"]) for radical in radical_definitions]
    selected_default = default_radical or radical_ids[0]
    if selected_default not in radical_ids:
        raise ValueError(
            f"defaultRadical {selected_default} is not in generated radicals"
        )

    return {
        "schemaVersion": SCHEMA_VERSION,
        "defaultRadical": selected_default,
        "radicals": [
            _site_index_radical(radical)
            for radical in radical_definitions
        ],
    }


def write_site_index(path: str | Path, site_index: Mapping[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(site_index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def public_radical_from_internal_group(
    group: Mapping[str, Any],
    radical_definition: Mapping[str, Any],
    *,
    reviewed_only: bool = False,
) -> dict[str, Any]:
    """Convert one internal radical group to the public radical JSON shape."""
    group_meta = group["group"]
    items = public_items_from_internal_group(group, reviewed_only=reviewed_only)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "id": group_meta["id"],
        "glyph": group_meta["glyph"],
        "title": radical_definition["title"],
        "copy": radical_definition["copy"],
        "tags": _combined_tags(radical_definition.get("tags", []), items),
        "items": items,
    }


def write_public_radical(
    path: str | Path,
    radical_json: Mapping[str, Any],
) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(radical_json, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def public_items_from_internal_group(
    group: Mapping[str, Any],
    *,
    reviewed_only: bool = False,
) -> list[dict[str, Any]]:
    """Convert internal items to the public item shape used by site JSON."""
    public_items: list[dict[str, Any]] = []
    for item in group.get("items", []):
        if reviewed_only and item.get("curationStatus") != "reviewed":
            continue
        public_items.append(_public_item(item))
    return public_items


def _public_item(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "char": item["char"],
        "name": item.get("name", ""),
        "meaning": item.get("meaning", ""),
        "readings": {
            "ja": list(item.get("readings", {}).get("ja", [])),
            "romaji": list(item.get("readings", {}).get("romaji", [])),
        },
        "unicode": item["unicode"],
        "jis": {
            "level": item["jis"]["level"],
            "kuten": item["jis"]["kuten"],
        },
        "parts": {
            "ja": item.get("parts", {}).get("ja", ""),
            "en": item.get("parts", {}).get("en", ""),
        },
        "note": item.get("note", ""),
        "tags": _unique_tags(item.get("tags", [])),
        "curationStatus": item.get("curationStatus", "unreviewed"),
    }


def _unique_tags(tags: Any) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        if not isinstance(tag, str) or tag == "All" or tag in seen:
            continue
        result.append(tag)
        seen.add(tag)
    return result


def _combined_tags(config_tags: Any, items: list[Mapping[str, Any]]) -> list[str]:
    combined = _unique_tags(config_tags)
    seen = set(combined)
    for item in items:
        for tag in _unique_tags(item.get("tags", [])):
            if tag not in seen:
                combined.append(tag)
                seen.add(tag)
    return combined


def _site_index_radical(radical: Mapping[str, Any]) -> dict[str, Any]:
    radical_id = str(radical["id"])
    return {
        "id": radical_id,
        "glyph": _glyph(radical),
        "labelJa": str(radical["labelJa"]),
        "labelEn": str(radical["labelEn"]),
        "file": f"radicals/{radical_id}.json",
        "theme": dict(radical["theme"]),
    }


def _glyph(radical: Mapping[str, Any]) -> str:
    return str(
        radical.get("glyph")
        or radical.get("displayRadical")
        or radical["radical"]
    )
