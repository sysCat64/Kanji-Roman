from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

ALLOWED_CURATION_STATUSES = {"reviewed", "draft", "unreviewed"}
RADICAL_ID_PATTERN = re.compile(r"^[a-z0-9-]+$")
VENDOR_README = Path("tools/json-generator/vendor/README.md")
VENDOR_README_REQUIRED_MARKERS = {
    "source URL": "https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip",
    "Unicode version": "Unicode version:",
    "retrieval status": "Retrieval status:",
    "license": "Unicode License v3",
}


def validate_project(root: str | Path) -> list[str]:
    """Validate repo JSON syntax and public site JSON contracts."""
    root_path = Path(root)
    issues: list[str] = []
    json_data: dict[Path, Any] = {}

    for path in json_files(root_path):
        try:
            json_data[path] = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(f"Invalid JSON in {_rel(path, root_path)}: {exc}")

    site_index = root_path / "data" / "site-index.json"
    if site_index.exists() and site_index in json_data:
        issues.extend(_validate_site_index(root_path, site_index, json_data[site_index]))

    radical_config = root_path / "tools" / "json-generator" / "config" / "radicals.json"
    if radical_config.exists() and radical_config in json_data:
        issues.extend(
            _validate_radical_config(root_path, radical_config, json_data[radical_config])
        )
        issues.extend(_validate_vendor_readme(root_path))

    return issues


def json_files(root: str | Path) -> list[Path]:
    root_path = Path(root)
    return sorted(
        path
        for path in root_path.rglob("*.json")
        if "node_modules" not in path.parts and ".git" not in path.parts
    )


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    root = Path(args[0]) if args else Path.cwd()
    issues = validate_project(root)
    if issues:
        for issue in issues:
            print(issue, file=sys.stderr)
        return 1
    print(f"Parsed {len(json_files(root))} JSON file(s)")
    return 0


def _validate_site_index(
    root: Path,
    site_index: Path,
    data: Any,
) -> list[str]:
    issues: list[str] = []
    rel_index = _rel(site_index, root)

    if not isinstance(data, Mapping):
        return [f"{rel_index} must be a JSON object"]

    required = {"schemaVersion", "defaultRadical", "radicals"}
    missing = sorted(required - set(data))
    if missing:
        issues.append(f"{rel_index} missing keys: {', '.join(missing)}")

    radicals = data.get("radicals", [])
    if not isinstance(radicals, list):
        return issues + [f"{rel_index} radicals must be an array"]

    seen_ids: set[str] = set()
    radical_ids: list[str] = []
    for radical in radicals:
        if not isinstance(radical, Mapping):
            issues.append(f"{rel_index} has non-object radical entry")
            continue
        rid = radical.get("id")
        if not isinstance(rid, str) or not rid:
            issues.append(f"{rel_index} has radical without id")
            continue
        if rid in seen_ids:
            issues.append(f"duplicate radical id: {rid}")
        seen_ids.add(rid)
        radical_ids.append(rid)
        issues.extend(_validate_site_index_radical(root, site_index, radical))

    default_radical = data.get("defaultRadical")
    if default_radical not in radical_ids:
        issues.append(f"{rel_index} defaultRadical is not listed: {default_radical}")

    return issues


def _validate_site_index_radical(
    root: Path,
    site_index: Path,
    radical: Mapping[str, Any],
) -> list[str]:
    issues: list[str] = []
    rid = str(radical.get("id", ""))
    file_value = radical.get("file")

    if not isinstance(file_value, str) or not file_value:
        return [f"radical {rid} missing file"]
    if file_value.startswith("/") or Path(file_value).is_absolute():
        issues.append(f"radical {rid} uses root-relative file path: {file_value}")
        return issues

    target = site_index.parent / file_value
    try:
        target.resolve().relative_to(site_index.parent.resolve())
    except ValueError:
        issues.append(f"radical {rid} file escapes data directory: {file_value}")
        return issues
    if not target.exists():
        issues.append(f"radical {rid} file does not exist: {_rel(target, root)}")
        return issues

    try:
        radical_data = json.loads(target.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"Invalid JSON in {_rel(target, root)}: {exc}"]

    issues.extend(_validate_public_radical(root, target, radical_data, expected_id=rid))
    return issues


def _validate_public_radical(
    root: Path,
    path: Path,
    data: Any,
    *,
    expected_id: str,
) -> list[str]:
    rel = _rel(path, root)
    issues: list[str] = []
    if not isinstance(data, Mapping):
        return [f"{rel} must be a JSON object"]

    required = {"schemaVersion", "id", "glyph", "title", "copy", "tags", "items"}
    missing = sorted(required - set(data))
    if missing:
        issues.append(f"{rel} missing keys: {', '.join(missing)}")
    if data.get("id") != expected_id:
        issues.append(f"{rel} id does not match site-index entry: {data.get('id')}")
    if "All" in data.get("tags", []):
        issues.append(f"{rel} includes forbidden tag 'All'")

    items = data.get("items", [])
    if not isinstance(items, list):
        return issues + [f"{rel} items must be an array"]

    chars: list[str] = []
    kuten_values: list[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            issues.append(f"{rel} item {index} must be an object")
            continue
        issues.extend(_validate_public_item(rel, index, item))
        char = item.get("char")
        if isinstance(char, str):
            chars.append(char)
        kuten = item.get("jis", {}).get("kuten") if isinstance(item.get("jis"), Mapping) else None
        if isinstance(kuten, str):
            kuten_values.append(kuten)

    duplicate_chars = _duplicates(chars)
    if duplicate_chars:
        issues.append(f"{rel} has duplicate chars: {', '.join(duplicate_chars)}")
    duplicate_kuten = _duplicates(kuten_values)
    if duplicate_kuten:
        issues.append(f"{rel} has duplicate jis.kuten: {', '.join(duplicate_kuten)}")

    return issues


def _validate_public_item(
    rel: str,
    index: int,
    item: Mapping[str, Any],
) -> list[str]:
    issues: list[str] = []
    prefix = f"{rel} item {index}"
    required = {
        "char",
        "name",
        "meaning",
        "readings",
        "unicode",
        "jis",
        "parts",
        "note",
        "tags",
        "curationStatus",
    }
    missing = sorted(required - set(item))
    if missing:
        issues.append(f"{prefix} missing keys: {', '.join(missing)}")
    char = item.get("char")
    if not isinstance(char, str) or len(char) != 1:
        issues.append(f"{prefix} char must be one character")

    unicode_value = item.get("unicode")
    if isinstance(char, str) and isinstance(unicode_value, str):
        expected_unicode = "U+" + format(ord(char), "04X")
        if unicode_value != expected_unicode:
            issues.append(
                f"{prefix} unicode mismatch: expected {expected_unicode}, got {unicode_value}"
            )
    else:
        issues.append(f"{prefix} unicode must be a string")

    jis = item.get("jis")
    if not isinstance(jis, Mapping):
        issues.append(f"{prefix} jis must be an object")
    else:
        if jis.get("level") not in (1, 2):
            issues.append(f"{prefix} invalid jis.level: {jis.get('level')}")
        kuten = jis.get("kuten")
        if not isinstance(kuten, str) or "-" not in kuten:
            issues.append(f"{prefix} invalid jis.kuten: {kuten}")

    curation_status = item.get("curationStatus")
    if curation_status not in ALLOWED_CURATION_STATUSES:
        issues.append(f"{prefix} invalid curationStatus: {curation_status}")
    if "All" in item.get("tags", []):
        issues.append(f"{prefix} includes forbidden tag 'All'")

    return issues


def _validate_radical_config(
    root: Path,
    path: Path,
    data: Any,
) -> list[str]:
    rel = _rel(path, root)
    if not isinstance(data, list):
        return [f"{rel} must be a JSON array"]

    issues: list[str] = []
    seen_ids: set[str] = set()
    for index, radical in enumerate(data):
        prefix = f"{rel} entry {index}"
        if not isinstance(radical, Mapping):
            issues.append(f"{prefix} must be an object")
            continue

        required = {
            "id",
            "glyph",
            "labelJa",
            "labelEn",
            "radical",
            "displayRadical",
            "kangxiRadicalNumber",
            "title",
            "copy",
            "tags",
            "theme",
        }
        missing = sorted(required - set(radical))
        if missing:
            issues.append(f"{prefix} missing keys: {', '.join(missing)}")

        radical_id = radical.get("id")
        if not isinstance(radical_id, str) or not RADICAL_ID_PATTERN.fullmatch(
            radical_id
        ):
            issues.append(f"{prefix} invalid radical id: {radical_id}")
        elif radical_id in seen_ids:
            issues.append(f"{rel} duplicate radical id: {radical_id}")
        else:
            seen_ids.add(radical_id)

        kangxi_number = radical.get("kangxiRadicalNumber")
        if not isinstance(kangxi_number, int) or not 1 <= kangxi_number <= 214:
            issues.append(f"{prefix} invalid kangxiRadicalNumber: {kangxi_number}")

        tags = radical.get("tags")
        if not isinstance(tags, list):
            issues.append(f"{prefix} tags must be an array")
        elif "All" in tags:
            issues.append(f"{prefix} includes forbidden tag 'All'")

        theme = radical.get("theme")
        if not isinstance(theme, Mapping):
            issues.append(f"{prefix} theme must be an object")
        else:
            required_theme = {"accent", "accentRgb", "darkAccent", "darkAccentRgb"}
            missing_theme = sorted(required_theme - set(theme))
            if missing_theme:
                issues.append(f"{prefix} theme missing keys: {', '.join(missing_theme)}")

    return issues


def _validate_vendor_readme(root: Path) -> list[str]:
    readme = root / VENDOR_README
    if not readme.exists():
        return [f"{VENDOR_README.as_posix()} is required"]

    text = readme.read_text(encoding="utf-8")
    issues: list[str] = []
    for label, marker in VENDOR_README_REQUIRED_MARKERS.items():
        if marker not in text:
            issues.append(f"{VENDOR_README.as_posix()} missing {label}")
    return issues


def _duplicates(values: list[str]) -> list[str]:
    return sorted({value for value in values if values.count(value) > 1})


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
