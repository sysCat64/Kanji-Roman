import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from kanji_roman_generator.radicals import (
    filter_jis_items_by_radical_id,
    load_radical_definitions,
)
from kanji_roman_generator.unihan import (
    load_krsunicode_from_zip,
    parse_krsunicode_text,
)


SAMPLE_KRSUNICODE = """\
# code point property value
U+9C06\tkRSUnicode\t195.9
U+6F01\tkRSUnicode\t85.11
U+9BAD\tkRSUnicode\t195.5 85.2
U+6728\tkDefinition\ttree
not a valid unihan row
"""


class UnihanParsingTest(unittest.TestCase):
    def test_parses_only_krsunicode_rows_to_kangxi_radical_numbers(self):
        records = parse_krsunicode_text(SAMPLE_KRSUNICODE)

        self.assertEqual((195,), records["鰆"])
        self.assertEqual((85,), records["漁"])
        self.assertEqual((195, 85), records[chr(0x9BAD)])
        self.assertNotIn("木", records)

    def test_loads_krsunicode_from_unihan_zip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "Unihan.zip"
            with zipfile.ZipFile(zip_path, "w") as archive:
                archive.writestr(
                    "Unihan_RadicalStrokeCounts.txt",
                    SAMPLE_KRSUNICODE,
                )

            records = load_krsunicode_from_zip(zip_path)

        self.assertEqual((195,), records["鰆"])
        self.assertEqual((85,), records["漁"])


class RadicalFilterTest(unittest.TestCase):
    def test_filters_jis_items_by_radical_id_from_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            radicals_path = Path(tmpdir) / "radicals.json"
            radicals_path.write_text(
                json.dumps(
                    [
                        {"id": "fish", "kangxiRadicalNumber": 195},
                        {"id": "water", "kangxiRadicalNumber": 85},
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            radical_definitions = load_radical_definitions(radicals_path)

        jis_items = [
            {"char": "鰆", "jis": {"kuten": "82-54"}},
            {"char": "漁", "jis": {"kuten": "21-89"}},
            {"char": chr(0x9BAD), "jis": {"kuten": "26-90"}},
            {"char": "木", "jis": {"kuten": "44-58"}},
        ]
        records = parse_krsunicode_text(SAMPLE_KRSUNICODE)

        fish_items = filter_jis_items_by_radical_id(
            jis_items,
            records,
            radical_definitions,
            "fish",
        )
        water_items = filter_jis_items_by_radical_id(
            jis_items,
            records,
            radical_definitions,
            "water",
        )

        self.assertEqual(
            ["鰆", chr(0x9BAD)],
            [item["char"] for item in fish_items],
        )
        self.assertEqual(
            ["漁", chr(0x9BAD)],
            [item["char"] for item in water_items],
        )

    def test_unknown_radical_id_is_reported(self):
        with self.assertRaisesRegex(ValueError, "unknown radical id"):
            filter_jis_items_by_radical_id([], {}, [], "missing")


if __name__ == "__main__":
    unittest.main()
