from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence


def load_radical_definitions(path: str | Path) -> list[dict[str, Any]]:
    """Load generator radical definitions from JSON."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("radical definitions must be a JSON array")
    return data


def find_radical_definition(
    radical_definitions: Sequence[Mapping[str, Any]],
    radical_id: str,
) -> Mapping[str, Any]:
    for radical in radical_definitions:
        if radical.get("id") == radical_id:
            return radical
    raise ValueError(f"unknown radical id: {radical_id}")


def filter_jis_items_by_radical_number(
    jis_items: Sequence[Mapping[str, Any]],
    radical_numbers_by_char: Mapping[str, Sequence[int]],
    kangxi_radical_number: int,
) -> list[Mapping[str, Any]]:
    """Return JIS items whose Unihan radical values include the target number."""
    filtered_items: list[Mapping[str, Any]] = []

    for item in jis_items:
        char = item.get("char")
        if not isinstance(char, str):
            continue
        if kangxi_radical_number in radical_numbers_by_char.get(char, ()):
            filtered_items.append(item)

    return filtered_items


def filter_jis_items_by_radical_id(
    jis_items: Sequence[Mapping[str, Any]],
    radical_numbers_by_char: Mapping[str, Sequence[int]],
    radical_definitions: Sequence[Mapping[str, Any]],
    radical_id: str,
) -> list[Mapping[str, Any]]:
    radical = find_radical_definition(radical_definitions, radical_id)
    try:
        kangxi_radical_number = int(radical["kangxiRadicalNumber"])
    except KeyError as exc:
        raise ValueError(
            f"radical {radical_id} missing kangxiRadicalNumber"
        ) from exc

    return filter_jis_items_by_radical_number(
        jis_items,
        radical_numbers_by_char,
        kangxi_radical_number,
    )
