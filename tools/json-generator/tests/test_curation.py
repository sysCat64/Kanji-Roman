import json
import tempfile
import unittest
from pathlib import Path

from kanji_roman_generator.curation import load_curation, merge_curation


BASE_ITEMS = [
    {
        "char": "鮭",
        "unicode": "U+9BAD",
        "codePoint": "9BAD",
        "jis": {"standard": "JIS X 0208", "level": 1, "kuten": "26-90"},
        "radical": {
            "char": "魚",
            "labelJa": "魚へん",
            "labelEn": "Fish radical",
            "kangxiRadicalNumber": 195,
        },
        "name": "",
        "meaning": "",
        "readings": {"ja": [], "romaji": []},
        "parts": {"ja": "", "en": ""},
        "note": "",
        "tags": [],
        "curationStatus": "unreviewed",
        "needsReview": False,
    },
    {
        "char": "鰆",
        "unicode": "U+9C06",
        "codePoint": "9C06",
        "jis": {"standard": "JIS X 0208", "level": 2, "kuten": "82-54"},
        "radical": {
            "char": "魚",
            "labelJa": "魚へん",
            "labelEn": "Fish radical",
            "kangxiRadicalNumber": 195,
        },
        "name": "",
        "meaning": "",
        "readings": {"ja": [], "romaji": []},
        "parts": {"ja": "", "en": ""},
        "note": "",
        "tags": [],
        "curationStatus": "unreviewed",
        "needsReview": False,
    },
]


class CurationLoadTest(unittest.TestCase):
    def test_loads_curation_input_by_character_key(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "fish.json"
            path.write_text(
                json.dumps(
                    {
                        "鰆": {
                            "name": "Japanese Spanish mackerel",
                            "meaning": "A spring-associated fish.",
                            "readings": {
                                "ja": ["さわら", "サワラ"],
                                "romaji": ["sawara"],
                            },
                            "parts": {"ja": "魚 + 春", "en": "Fish + Spring"},
                            "note": "Draft wording.",
                            "tags": ["fish", "spring", "food"],
                            "curationStatus": "draft",
                            "needsReview": True,
                            "sourceLabel": "Example dictionary",
                            "sourceUrl": "https://example.com/sawara",
                            "sourceCheckedAt": "2026-06-23",
                            "reviewNote": "Readings and English display name checked.",
                        }
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            curation = load_curation(path)

        self.assertEqual("Japanese Spanish mackerel", curation["鰆"]["name"])
        self.assertEqual(["sawara"], curation["鰆"]["readings"]["romaji"])
        self.assertTrue(curation["鰆"]["needsReview"])
        self.assertEqual("Example dictionary", curation["鰆"]["sourceLabel"])
        self.assertEqual("https://example.com/sawara", curation["鰆"]["sourceUrl"])
        self.assertEqual("2026-06-23", curation["鰆"]["sourceCheckedAt"])
        self.assertEqual(
            "Readings and English display name checked.",
            curation["鰆"]["reviewNote"],
        )

    def test_rejects_invalid_curation_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "fish.json"
            path.write_text(
                json.dumps(
                    {
                        "鰆": {
                            "readings": {"ja": "さわら", "romaji": []},
                            "tags": ["All"],
                            "curationStatus": "done",
                        }
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "readings.ja"):
                load_curation(path)

    def test_rejects_non_kanji_curation_key(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "fish.json"
            path.write_text(
                json.dumps({"A": {"name": "Letter A"}}, ensure_ascii=False),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "one kanji character"):
                load_curation(path)


class CurationMergeTest(unittest.TestCase):
    def test_merges_curation_fields_and_keeps_unreviewed_defaults(self):
        result = merge_curation(
            BASE_ITEMS,
            {
                "鰆": {
                    "name": "Japanese Spanish mackerel",
                    "meaning": "A spring-associated fish.",
                    "readings": {
                        "ja": ["さわら", "サワラ"],
                        "romaji": ["sawara"],
                    },
                    "parts": {"ja": "魚 + 春", "en": "Fish + Spring"},
                    "note": "Draft wording.",
                    "tags": ["fish", "spring", "fish"],
                    "curationStatus": "draft",
                    "needsReview": True,
                    "sourceLabel": "Example dictionary",
                    "sourceUrl": "https://example.com/sawara",
                    "sourceCheckedAt": "2026-06-23",
                    "reviewNote": "Draft source check.",
                }
            },
        )

        salmon, sawara = result.items

        self.assertEqual("unreviewed", salmon["curationStatus"])
        self.assertEqual("", salmon["name"])
        self.assertEqual([], salmon["readings"]["ja"])
        self.assertFalse(salmon["needsReview"])

        self.assertEqual("Japanese Spanish mackerel", sawara["name"])
        self.assertEqual("A spring-associated fish.", sawara["meaning"])
        self.assertEqual(["さわら", "サワラ"], sawara["readings"]["ja"])
        self.assertEqual(["sawara"], sawara["readings"]["romaji"])
        self.assertEqual({"ja": "魚 + 春", "en": "Fish + Spring"}, sawara["parts"])
        self.assertEqual("Draft wording.", sawara["note"])
        self.assertEqual(["fish", "spring"], sawara["tags"])
        self.assertEqual("draft", sawara["curationStatus"])
        self.assertTrue(sawara["needsReview"])
        self.assertEqual("Example dictionary", sawara["sourceLabel"])
        self.assertEqual("https://example.com/sawara", sawara["sourceUrl"])
        self.assertEqual("2026-06-23", sawara["sourceCheckedAt"])
        self.assertEqual("Draft source check.", sawara["reviewNote"])
        self.assertEqual([], result.warnings)

    def test_reports_out_of_scope_curation_without_blocking_generation(self):
        result = merge_curation(
            BASE_ITEMS,
            {
                "鰆": {"name": "Japanese Spanish mackerel"},
                "鮪": {"name": "Tuna", "curationStatus": "reviewed"},
            },
        )

        self.assertEqual(["鮭", "鰆"], [item["char"] for item in result.items])
        self.assertEqual(
            [
                {
                    "type": "curation-out-of-scope",
                    "char": "鮪",
                    "message": "curation entry for 鮪 is not in generated items",
                }
            ],
            result.warnings,
        )


if __name__ == "__main__":
    unittest.main()
