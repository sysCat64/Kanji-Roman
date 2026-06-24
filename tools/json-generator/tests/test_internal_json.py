import contextlib
import io
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

    def test_merges_curation_into_internal_group_and_reports_warnings(self):
        group = generate_internal_group(
            "fish",
            RADICALS,
            {"鰆": (195,), "漁": (85,), "鮭": (195, 85)},
            jis_items=SAMPLE_JIS_ITEMS,
            generated_at="2026-06-23T00:00:00+09:00",
            unihan_source_file="test.zip",
            curation_by_char={
                "鰆": {
                    "name": "Japanese Spanish mackerel",
                    "meaning": "A spring-associated fish.",
                    "readings": {
                        "ja": ["さわら", "サワラ"],
                        "romaji": ["sawara"],
                    },
                    "parts": {"ja": "魚 + 春", "en": "Fish + 春 component"},
                    "note": "Draft wording.",
                    "tags": ["fish", "spring"],
                    "curationStatus": "draft",
                    "needsReview": True,
                },
                "鮪": {
                    "name": "Tuna",
                    "curationStatus": "reviewed",
                },
            },
        )

        salmon, sawara = group["items"]

        self.assertEqual("unreviewed", salmon["curationStatus"])
        self.assertEqual("Japanese Spanish mackerel", sawara["name"])
        self.assertEqual(["さわら", "サワラ"], sawara["readings"]["ja"])
        self.assertEqual("draft", sawara["curationStatus"])
        self.assertTrue(sawara["needsReview"])
        self.assertEqual(
            [
                {
                    "type": "curation-out-of-scope",
                    "char": "鮪",
                    "message": "curation entry for 鮪 is not in generated items",
                }
            ],
            group["warnings"],
        )


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

    def test_cli_loads_curation_dir_for_internal_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            radicals_path = root / "radicals.json"
            unihan_path = root / "Unihan.zip"
            curation_dir = root / "curation"
            out_dir = root / "outputs"
            radicals_path.write_text(
                json.dumps(RADICALS, ensure_ascii=False),
                encoding="utf-8",
            )
            curation_dir.mkdir()
            (curation_dir / "fish.json").write_text(
                json.dumps(
                    {
                        "鰆": {
                            "name": "Japanese Spanish mackerel",
                            "meaning": "A spring-associated fish.",
                            "readings": {
                                "ja": ["さわら", "サワラ"],
                                "romaji": ["sawara"],
                            },
                            "parts": {"ja": "魚 + 春", "en": "Fish + 春 component"},
                            "note": "Draft wording.",
                            "tags": ["fish", "spring"],
                            "curationStatus": "draft",
                            "needsReview": True,
                        },
                        "鮪": {
                            "name": "Tuna",
                            "curationStatus": "draft",
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            with zipfile.ZipFile(unihan_path, "w") as archive:
                archive.writestr(
                    "Unihan_RadicalStrokeCounts.txt",
                    SAMPLE_KRSUNICODE,
                )

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = main(
                    [
                        "--radical",
                        "fish",
                        "--radicals",
                        str(radicals_path),
                        "--unihan",
                        str(unihan_path),
                        "--curation-dir",
                        str(curation_dir),
                        "--out-dir",
                        str(out_dir),
                    ]
                )

            output = json.loads((out_dir / "fish.json").read_text(encoding="utf-8"))

        self.assertEqual(0, exit_code)
        self.assertEqual("Japanese Spanish mackerel", output["items"][1]["name"])
        self.assertEqual("draft", output["items"][1]["curationStatus"])
        self.assertEqual("鮪", output["warnings"][0]["char"])
        self.assertIn("curation entry for 鮪", stderr.getvalue())

    def test_cli_writes_reviewed_only_public_radical_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            radicals_path = root / "radicals.json"
            unihan_path = root / "Unihan.zip"
            curation_dir = root / "curation"
            out_dir = root / "outputs"
            site_data_dir = root / "data"
            radicals_path.write_text(
                json.dumps(RADICALS, ensure_ascii=False),
                encoding="utf-8",
            )
            curation_dir.mkdir()
            (curation_dir / "fish.json").write_text(
                json.dumps(
                    {
                        "鮭": {
                            "name": "Chum salmon",
                            "curationStatus": "reviewed",
                            "needsReview": False,
                            "sourceLabel": "Example dictionary",
                            "sourceCheckedAt": "2026-06-23",
                        },
                        "鰆": {
                            "name": "Japanese Spanish mackerel",
                            "curationStatus": "draft",
                        },
                    },
                    ensure_ascii=False,
                ),
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
                    str(curation_dir),
                    "--out-dir",
                    str(out_dir),
                    "--site-data-dir",
                    str(site_data_dir),
                    "--reviewed-only",
                ]
            )

            internal_output = json.loads(
                (out_dir / "fish.json").read_text(encoding="utf-8")
            )
            public_output = json.loads(
                (site_data_dir / "radicals" / "fish.json").read_text(
                    encoding="utf-8"
                )
            )
            site_index = json.loads(
                (site_data_dir / "site-index.json").read_text(encoding="utf-8")
            )

        self.assertEqual(0, exit_code)
        self.assertEqual(["鮭", "鰆"], [item["char"] for item in internal_output["items"]])
        self.assertEqual("fish", site_index["defaultRadical"])
        self.assertEqual(["fish"], [radical["id"] for radical in site_index["radicals"]])
        self.assertEqual("radicals/fish.json", site_index["radicals"][0]["file"])
        self.assertEqual(["鮭"], [item["char"] for item in public_output["items"]])
        self.assertNotIn("needsReview", public_output["items"][0])

    def test_cli_writes_curation_coverage_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            radicals_path = root / "radicals.json"
            unihan_path = root / "Unihan.zip"
            curation_dir = root / "curation"
            out_dir = root / "outputs"
            report_path = root / "coverage.json"
            radicals_path.write_text(
                json.dumps(RADICALS, ensure_ascii=False),
                encoding="utf-8",
            )
            curation_dir.mkdir()
            (curation_dir / "fish.json").write_text(
                json.dumps(
                    {
                        "鮭": {
                            "name": "Chum salmon",
                            "curationStatus": "reviewed",
                            "needsReview": False,
                            "sourceLabel": "Example dictionary",
                            "sourceCheckedAt": "2026-06-23",
                        },
                        "鰆": {
                            "name": "Japanese Spanish mackerel",
                            "curationStatus": "draft",
                        },
                    },
                    ensure_ascii=False,
                ),
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
                    "--curation-dir",
                    str(curation_dir),
                    "--out-dir",
                    str(out_dir),
                    "--coverage-report",
                    str(report_path),
                ]
            )

            report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(0, exit_code)
        self.assertEqual(
            {
                "schemaVersion": "0.1",
                "radicals": [
                    {
                        "id": "fish",
                        "total": 2,
                        "reviewed": 1,
                        "draft": 1,
                        "unreviewed": 0,
                    },
                    {
                        "id": "water",
                        "total": 2,
                        "reviewed": 0,
                        "draft": 0,
                        "unreviewed": 2,
                    },
                ],
            },
            report,
        )

    def test_cli_all_writes_public_site_index_for_every_generated_radical(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            radicals_path = root / "radicals.json"
            unihan_path = root / "Unihan.zip"
            out_dir = root / "outputs"
            site_data_dir = root / "data"
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
                    "--site-data-dir",
                    str(site_data_dir),
                    "--default-radical",
                    "water",
                ]
            )

            site_index = json.loads(
                (site_data_dir / "site-index.json").read_text(encoding="utf-8")
            )
            fish_public_exists = (site_data_dir / "radicals" / "fish.json").exists()
            water_public_exists = (site_data_dir / "radicals" / "water.json").exists()

        self.assertEqual(0, exit_code)
        self.assertEqual("water", site_index["defaultRadical"])
        self.assertEqual(
            ["fish", "water"],
            [radical["id"] for radical in site_index["radicals"]],
        )
        self.assertTrue(fish_public_exists)
        self.assertTrue(water_public_exists)

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
