from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

ALLOWED_CURATION_STATUSES = {"reviewed", "draft", "unreviewed"}


@dataclass(frozen=True)
class CurationMergeResult:
    items: list[dict[str, Any]]
    warnings: list[dict[str, str]]


def load_curation(path: str | Path) -> dict[str, dict[str, Any]]:
    """Load one radical curation file keyed by kanji character."""
    curation_path = Path(path)
    if not curation_path.exists():
        return {}

    data = json.loads(curation_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{curation_path} must contain a JSON object")

    curation: dict[str, dict[str, Any]] = {}
    for char, entry in data.items():
        _validate_char_key(char)
        if not isinstance(entry, dict):
            raise ValueError(f"curation entry for {char} must be an object")
        curation[char] = _normalize_entry(char, entry)

    return curation


def merge_curation(
    items: Sequence[Mapping[str, Any]],
    curation_by_char: Mapping[str, Mapping[str, Any]],
) -> CurationMergeResult:
    """Merge human curation fields into generated JIS/Unihan items."""
    generated_chars = {
        item["char"]
        for item in items
        if isinstance(item.get("char"), str)
    }
    warnings = [
        _out_of_scope_warning(char)
        for char in curation_by_char
        if char not in generated_chars
    ]

    merged_items: list[dict[str, Any]] = []
    for item in items:
        merged_item = _with_curation_defaults(dict(item))
        char = str(merged_item["char"])
        if char in curation_by_char:
            curation = _normalize_entry(char, curation_by_char[char])
            merged_item.update(
                {
                    "name": curation["name"],
                    "meaning": curation["meaning"],
                    "readings": curation["readings"],
                    "parts": curation["parts"],
                    "note": curation["note"],
                    "tags": curation["tags"],
                    "curationStatus": curation["curationStatus"],
                    "needsReview": curation["needsReview"],
                }
            )
        merged_items.append(merged_item)

    return CurationMergeResult(items=merged_items, warnings=warnings)


def _normalize_entry(
    char: str,
    entry: Mapping[str, Any],
) -> dict[str, Any]:
    readings = _normalize_readings(char, entry.get("readings", {}))
    parts = _normalize_parts(char, entry.get("parts", {}))
    tags = _unique_strings_without_all(char, "tags", entry.get("tags", []))
    curation_status = entry.get("curationStatus", "draft")
    if curation_status not in ALLOWED_CURATION_STATUSES:
        raise ValueError(
            f"curation entry for {char} has invalid curationStatus: "
            f"{curation_status}"
        )

    return {
        "name": _string_field(char, entry, "name"),
        "meaning": _string_field(char, entry, "meaning"),
        "readings": readings,
        "parts": parts,
        "note": _string_field(char, entry, "note"),
        "tags": tags,
        "curationStatus": curation_status,
        "needsReview": _bool_field(char, entry, "needsReview"),
    }


def _with_curation_defaults(item: dict[str, Any]) -> dict[str, Any]:
    item.setdefault("name", "")
    item.setdefault("meaning", "")
    item.setdefault("readings", {"ja": [], "romaji": []})
    item.setdefault("parts", {"ja": "", "en": ""})
    item.setdefault("note", "")
    item.setdefault("tags", [])
    item.setdefault("curationStatus", "unreviewed")
    item.setdefault("needsReview", False)
    item["readings"] = _normalize_readings(str(item["char"]), item["readings"])
    item["parts"] = _normalize_parts(str(item["char"]), item["parts"])
    item["tags"] = _unique_strings_without_all(str(item["char"]), "tags", item["tags"])
    return item


def _normalize_readings(char: str, value: Any) -> dict[str, list[str]]:
    if value is None:
        value = {}
    if not isinstance(value, Mapping):
        raise ValueError(f"curation entry for {char} readings must be an object")
    return {
        "ja": _string_list(char, "readings.ja", value.get("ja", [])),
        "romaji": _string_list(char, "readings.romaji", value.get("romaji", [])),
    }


def _normalize_parts(char: str, value: Any) -> dict[str, str]:
    if value is None:
        value = {}
    if not isinstance(value, Mapping):
        raise ValueError(f"curation entry for {char} parts must be an object")
    return {
        "ja": _optional_string(char, "parts.ja", value.get("ja", "")),
        "en": _optional_string(char, "parts.en", value.get("en", "")),
    }


def _string_field(
    char: str,
    entry: Mapping[str, Any],
    field: str,
) -> str:
    return _optional_string(char, field, entry.get(field, ""))


def _optional_string(char: str, field: str, value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError(f"curation entry for {char} {field} must be a string")
    return value


def _bool_field(
    char: str,
    entry: Mapping[str, Any],
    field: str,
) -> bool:
    value = entry.get(field, False)
    if not isinstance(value, bool):
        raise ValueError(f"curation entry for {char} {field} must be a boolean")
    return value


def _string_list(char: str, field: str, value: Any) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"curation entry for {char} {field} must be an array")
    if not all(isinstance(item, str) for item in value):
        raise ValueError(f"curation entry for {char} {field} must contain strings")
    return list(value)


def _unique_strings_without_all(char: str, field: str, value: Any) -> list[str]:
    values = _string_list(char, field, value)
    result: list[str] = []
    seen: set[str] = set()
    for item in values:
        if item == "All":
            raise ValueError(f"curation entry for {char} {field} must not contain All")
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def _validate_char_key(char: Any) -> None:
    if not isinstance(char, str) or len(char) != 1 or not _is_cjk_kanji(char):
        raise ValueError(f"curation key must be one kanji character: {char}")


def _out_of_scope_warning(char: str) -> dict[str, str]:
    return {
        "type": "curation-out-of-scope",
        "char": char,
        "message": f"curation entry for {char} is not in generated items",
    }


def _is_cjk_kanji(char: str) -> bool:
    code_point = ord(char)
    return (
        0x3400 <= code_point <= 0x4DBF
        or 0x4E00 <= code_point <= 0x9FFF
        or 0xF900 <= code_point <= 0xFAFF
        or 0x20000 <= code_point <= 0x2A6DF
        or 0x2A700 <= code_point <= 0x2B73F
        or 0x2B740 <= code_point <= 0x2B81F
        or 0x2B820 <= code_point <= 0x2CEAF
        or 0x2CEB0 <= code_point <= 0x2EBEF
        or 0x30000 <= code_point <= 0x3134F
    )
