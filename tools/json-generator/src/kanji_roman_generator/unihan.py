from __future__ import annotations

import re
import zipfile
from pathlib import Path

UNIHAN_RADICAL_STROKE_COUNTS = "Unihan_RadicalStrokeCounts.txt"
KRSUNICODE_PROPERTY = "kRSUnicode"
_RADICAL_NUMBER_PATTERN = re.compile(r"^(\d{1,3})'?\.")


def radical_numbers_from_krsunicode(value: str) -> tuple[int, ...]:
    """Extract Kangxi radical numbers from a kRSUnicode property value."""
    numbers: list[int] = []
    seen: set[int] = set()

    for token in value.split():
        match = _RADICAL_NUMBER_PATTERN.match(token)
        if not match:
            continue
        number = int(match.group(1))
        if number not in seen:
            numbers.append(number)
            seen.add(number)

    return tuple(numbers)


def parse_krsunicode_text(text: str) -> dict[str, tuple[int, ...]]:
    """Parse Unihan_RadicalStrokeCounts text into char to radical numbers."""
    records: dict[str, tuple[int, ...]] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split(None, 2)
        if len(parts) != 3:
            continue

        code_point, property_name, value = parts
        if property_name != KRSUNICODE_PROPERTY:
            continue

        radical_numbers = radical_numbers_from_krsunicode(value)
        if radical_numbers:
            records[_char_from_code_point(code_point)] = radical_numbers

    return records


def load_krsunicode_from_zip(path: str | Path) -> dict[str, tuple[int, ...]]:
    """Load kRSUnicode records from a local Unihan.zip file."""
    with zipfile.ZipFile(path) as archive:
        try:
            raw_text = archive.read(UNIHAN_RADICAL_STROKE_COUNTS)
        except KeyError as exc:
            raise FileNotFoundError(
                f"{UNIHAN_RADICAL_STROKE_COUNTS} not found in {path}"
            ) from exc

    return parse_krsunicode_text(raw_text.decode("utf-8"))


def _char_from_code_point(value: str) -> str:
    if not value.startswith("U+"):
        raise ValueError(f"invalid Unihan code point: {value}")
    return chr(int(value[2:], 16))
