import unittest

from kanji_roman_generator.site_json import (
    public_items_from_internal_group,
    public_radical_from_internal_group,
)


class SiteJsonCurationTest(unittest.TestCase):
    def test_public_radical_json_reflects_merged_curation_fields(self):
        group = {
            "group": {"id": "fish", "glyph": "魚"},
            "items": [
                {
                    "char": "鰆",
                    "name": "Japanese Spanish mackerel",
                    "meaning": "A spring-associated fish.",
                    "readings": {"ja": ["さわら"], "romaji": ["sawara"]},
                    "unicode": "U+9C06",
                    "jis": {"level": 2, "kuten": "82-54"},
                    "parts": {"ja": "魚 + 春", "en": "Fish + Spring"},
                    "note": "Draft wording.",
                    "tags": ["spring", "food"],
                    "curationStatus": "draft",
                    "needsReview": True,
                }
            ],
        }
        radical = {
            "title": "魚へんの漢字",
            "copy": "辞書上の部首が魚に分類されるJIS第一・第二水準の漢字。",
            "tags": ["fish", "food"],
        }

        public_json = public_radical_from_internal_group(group, radical)

        self.assertEqual("0.1", public_json["schemaVersion"])
        self.assertEqual("fish", public_json["id"])
        self.assertEqual("魚", public_json["glyph"])
        self.assertEqual("魚へんの漢字", public_json["title"])
        self.assertEqual(["fish", "food", "spring"], public_json["tags"])
        self.assertEqual(
            "Japanese Spanish mackerel",
            public_json["items"][0]["name"],
        )
        self.assertNotIn("needsReview", public_json["items"][0])

    def test_public_items_reflect_merged_curation_fields(self):
        group = {
            "items": [
                {
                    "char": "鰆",
                    "name": "Japanese Spanish mackerel",
                    "meaning": "A spring-associated fish.",
                    "readings": {"ja": ["さわら"], "romaji": ["sawara"]},
                    "unicode": "U+9C06",
                    "jis": {"level": 2, "kuten": "82-54"},
                    "parts": {"ja": "魚 + 春", "en": "Fish + Spring"},
                    "note": "Draft wording.",
                    "tags": ["fish", "spring"],
                    "curationStatus": "draft",
                    "needsReview": True,
                }
            ]
        }

        public_items = public_items_from_internal_group(group)

        self.assertEqual(
            [
                {
                    "char": "鰆",
                    "name": "Japanese Spanish mackerel",
                    "meaning": "A spring-associated fish.",
                    "readings": {"ja": ["さわら"], "romaji": ["sawara"]},
                    "unicode": "U+9C06",
                    "jis": {"level": 2, "kuten": "82-54"},
                    "parts": {"ja": "魚 + 春", "en": "Fish + Spring"},
                    "note": "Draft wording.",
                    "tags": ["fish", "spring"],
                    "curationStatus": "draft",
                }
            ],
            public_items,
        )

    def test_reviewed_only_keeps_only_reviewed_items_for_public_output(self):
        group = {
            "items": [
                {
                    "char": "鮭",
                    "name": "Salmon",
                    "meaning": "",
                    "readings": {"ja": [], "romaji": []},
                    "unicode": "U+9BAD",
                    "jis": {"level": 1, "kuten": "26-90"},
                    "parts": {"ja": "", "en": ""},
                    "note": "",
                    "tags": [],
                    "curationStatus": "reviewed",
                    "needsReview": False,
                },
                {
                    "char": "鰆",
                    "name": "Japanese Spanish mackerel",
                    "meaning": "",
                    "readings": {"ja": [], "romaji": []},
                    "unicode": "U+9C06",
                    "jis": {"level": 2, "kuten": "82-54"},
                    "parts": {"ja": "", "en": ""},
                    "note": "",
                    "tags": [],
                    "curationStatus": "draft",
                    "needsReview": True,
                },
            ]
        }

        public_items = public_items_from_internal_group(group, reviewed_only=True)

        self.assertEqual(["鮭"], [item["char"] for item in public_items])


if __name__ == "__main__":
    unittest.main()
