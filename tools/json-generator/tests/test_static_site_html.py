import unittest
from pathlib import Path


class StaticSiteHtmlTest(unittest.TestCase):
    def setUp(self):
        self.html = Path("design/radical-kanji-ui.html").read_text(encoding="utf-8")

    def test_ui_loads_public_json_instead_of_inline_collections(self):
        self.assertNotIn("const collections = {", self.html)
        self.assertIn("../data/site-index.json", self.html)
        self.assertIn("fetchJson", self.html)
        self.assertIn("loadSiteIndex", self.html)
        self.assertIn("loadRadical", self.html)

    def test_ui_renders_public_json_item_fields(self):
        self.assertIn("item.readings", self.html)
        self.assertIn("item.parts", self.html)
        self.assertIn("item.jis", self.html)
        self.assertNotIn("partsJa", self.html)
        self.assertNotIn("partsEn", self.html)
        self.assertNotIn("item.reading.join", self.html)


if __name__ == "__main__":
    unittest.main()
