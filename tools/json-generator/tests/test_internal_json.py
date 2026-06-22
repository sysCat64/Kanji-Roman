import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from kanji_roman_generator.cli import main
from kanji_roman_generator.internal_json import generate_internal_group


RADICALS = [
    {
        "id": "fish",
        "glyph": "魚",
        "labelJa": "魚へん",
        "labelEn": "Fish radical",
        "radical": "魚",
        "displayRadical": "魚",
        "kangxiRadicalNumber": 195,
        "title": "魚へんの漢字",
        "copy": "辞書上の部首が魚に分類されるJIS第一・第二水準の漢字。",
        "tags": ["fish", "seafood", "sushi"],
        "theme": {
            "accent": "#0f766e",
            "accentRgb": "15 118 110",
            "darkAccent": "#5eead4",
            "darkAccentRgb": "94 234 212",
        },
    },
    {
        "id": "water",
        "glyph": "水",
        "labelJa": "水へん",
        "labelEn": "Water radical",
        "radical": "水",
        "displayRadical": "水",
        "kangxiRadicalNumber": 85,
        "title": "水へんの漢字",
        "copy": "辞書上の部首が水に分類されるJIS第一・第二水準の漢字。",
        "tags": ["water"],
        "theme": {
            "accent": "#2563eb",
            "accentRgb": "37 99 235",
            "darkAccent": "#93c5fd",
            "darkAccentRgb": "147 197 253",
        },
    },
]

SAMPLE_JIS_ITEMS = [
    {
        "char": "鰆",
        "unicode": "U+9C06",
        "codePoint": "9C06",
        "jis": {
            "standard": "JIS X 0208",
            "level": 2,
            "kuten": "82-54",
        },
    },
    {
        "char": "漁",
        "unicode": "U+6F01",
        "codePoint": "6F01",
        "jis": {
            "standard": "JIS X 0208",
            "level": 1,
            "kuten": "21-89",
        },
    },
    {
        "char": "鮭",
        "unicode": "U+9BAD",
        "codePoint": "9BAD",
        "jis": {
            "standard": "JIS X 0208",
            "level": 1,
            "kuten": "26-90",
        },
    },
]

SAMPLE_KRSUNICODE = """\
U+9C06\tkRSUnicode\t195.9
U+6F01\tkRSUnicode\t85.11
U+9BAD\tkRSUnicode\t195.5 85.2
"""


class InternalJsonGenerationTest(unittest.TestCase):
    def test_generates_internal_group_from_jis_unihan_and_radical_definition(self):
        group = generate_internal_group(
            "fish",
            RADICALS,
            {"鰆": (195,), "漁": (85,), "鮭": (195, 85)},
            jis_items=SAMPLE_JIS_ITEMS,
            generated_at="2026-06-23T00:00:00+09:00",
            unihan_source_file="tools/json-generator/vendor/Unihan.zip",
        )

        self.assertEqual("0.1", group["schemaVersion"])
        self.assertEqual("2026-06-23T00:00:00+09:00", group["generatedAt"])
        self.assertEqual(
            {
                "characterSet": "JIS X 0208 Level 1 and Level 2",
                "jisMethod": "EUC-JP decode from kuten rows 16-84",
                "unihan": {
                    "property": "kRSUnicode",
                    "sourceFile": "tools/json-generator/vendor/Unihan.zip",
                },
            },
            group["source"],
        )
        self.assertEqual(
            {
                "id": "fish",
                "glyph": "魚",
                "labelJa": "魚へん",
                "labelEn": "Fish radical",
                "kangxiRadicalNumber": 195,
            },
            group["group"],
        )
        self.assertEqual(["鮭", "鰆"], [item["char"] for item in group["items"]])
        self.assertEqual(
            {
                "char": "魚",
                "labelJa": "魚へん",
                "labelEn": "Fish radical",
                "kangxiRadicalNumber": 195,
            },
            group["items"][1]["radical"],
        )
        self.assertEqual("", group["items"][1]["name"])
        self.assertEqual("", group["items"][1]["meaning"])
        self.assertEqual({"ja": [], "romaji": []}, group["items"][1]["readings"])
        self.assertEqual({"ja": "", "en": ""}, group["items"][1]["parts"])
        self.assertEqual("unreviewed", group["items"][1]["curationStatus"])
        self.assertFalse(group["items"][1]["needsReview"])

    def test_can_sort_internal_items_by_unicode(self):
        group = generate_internal_group(
            "fish",
            RADICALS,
            {"鰆": (195,), "鮭": (195,)},
            jis_items=list(reversed(SAMPLE_JIS_ITEMS)),
            sort_order="unicode",
            generated_at="2026-06-23T00:00:00+09:00",
            unihan_source_file="test.zip",
        )

        self.assertEqual(["鮭", "鰆"], [item["char"] for item in group["items"]])


class InternalJsonCliTest(unittest.TestCase):
    def test_cli_writes_single_radical_internal_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            radicals_path = root / "radicals.json"
            unihan_path = root / "Unihan.zip"
            out_dir = root / "outputs"
            radicals_path.write_text(
                json.dumps(RADICALS, ensure_ascii=False),
                encoding="utf-8",
            )
            with zipfile.ZipFile(unihan_path, "w") as archive:
                archive.writestr(
                    "Unihan_RadicalStrokeCounts.txt",
                    SAMPLE_KRSUNICODE,
                )

            exit_code = main(
                [
                    "--radical",
                    "fish",
                    "--radicals",
                    str(radicals_path),
                    "--unihan",
                    str(unihan_path),
                    "--curation-dir",
                    str(root / "curation"),
                    "--out-dir",
                    str(out_dir),
                    "--site-data-dir",
                    str(root / "data"),
                    "--default-radical",
                    "fish",
                ]
            )

            output = json.loads((out_dir / "fish.json").read_text(encoding="utf-8"))

        self.assertEqual(0, exit_code)
        self.assertEqual("fish", output["group"]["id"])
        self.assertEqual(["鮭", "鰆"], [item["char"] for item in output["items"]])

    def test_cli_all_writes_every_radical_definition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            radicals_path = root / "radicals.json"
            unihan_path = root / "Unihan.zip"
            out_dir = root / "outputs"
            radicals_path.write_text(
                json.dumps(RADICALS, ensure_ascii=False),
                encoding="utf-8",
            )
            with zipfile.ZipFile(unihan_path, "w") as archive:
                archive.writestr(
                    "Unihan_RadicalStrokeCounts.txt",
                    SAMPLE_KRSUNICODE,
                )

            exit_code = main(
                [
                    "--all",
                    "--radicals",
                    str(radicals_path),
                    "--unihan",
                    str(unihan_path),
                    "--out-dir",
                    str(out_dir),
                    "--sort",
                    "unicode",
                ]
            )

            fish = json.loads((out_dir / "fish.json").read_text(encoding="utf-8"))
            water = json.loads((out_dir / "water.json").read_text(encoding="utf-8"))

        self.assertEqual(0, exit_code)
        self.assertEqual(["鮭", "鰆"], [item["char"] for item in fish["items"]])
        self.assertEqual(["漁", "鮭"], [item["char"] for item in water["items"]])


if __name__ == "__main__":
    unittest.main()
