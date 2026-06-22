import re
import unittest

from kanji_roman_generator.jis import enumerate_jis_x0208_kanji


class JisEnumerationTest(unittest.TestCase):
    def test_enumerates_jis_x0208_level_one_and_two_kanji(self):
        items = enumerate_jis_x0208_kanji()
        by_kuten = {item["jis"]["kuten"]: item for item in items}

        self.assertEqual(6355, len(items))
        self.assertEqual(2965, sum(1 for item in items if item["jis"]["level"] == 1))
        self.assertEqual(3390, sum(1 for item in items if item["jis"]["level"] == 2))
        self.assertEqual(
            {
                "char": "亜",
                "unicode": "U+4E9C",
                "codePoint": "4E9C",
                "jis": {
                    "standard": "JIS X 0208",
                    "level": 1,
                    "kuten": "16-01",
                },
            },
            by_kuten["16-01"],
        )
        self.assertEqual(
            {
                "char": "弌",
                "unicode": "U+5F0C",
                "codePoint": "5F0C",
                "jis": {
                    "standard": "JIS X 0208",
                    "level": 2,
                    "kuten": "48-01",
                },
            },
            by_kuten["48-01"],
        )
        self.assertEqual("熙", items[-1]["char"])
        self.assertEqual("84-06", items[-1]["jis"]["kuten"])

    def test_emits_valid_unicode_kuten_level_and_unique_chars(self):
        items = enumerate_jis_x0208_kanji()
        seen_chars = set()
        kuten_pattern = re.compile(r"^\d{2}-\d{2}$")

        for item in items:
            char = item["char"]
            self.assertNotIn(char, seen_chars)
            seen_chars.add(char)

            expected_code_point = f"{ord(char):04X}"
            self.assertEqual(f"U+{expected_code_point}", item["unicode"])
            self.assertEqual(expected_code_point, item["codePoint"])
            self.assertRegex(item["jis"]["kuten"], kuten_pattern)
            self.assertIn(item["jis"]["level"], {1, 2})


if __name__ == "__main__":
    unittest.main()
