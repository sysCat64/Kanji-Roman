import unittest
from pathlib import Path


class StaticSiteHtmlTest(unittest.TestCase):
    def setUp(self):
        self.html = Path("design/radical-kanji-ui.html").read_text(encoding="utf-8")

    def assertHtmlContains(self, snippet):
        self.assertTrue(snippet in self.html, f"Expected HTML to contain {snippet!r}")

    def test_ui_loads_public_json_instead_of_inline_collections(self):
        self.assertNotIn("const collections = {", self.html)
        self.assertIn("../data/site-index.json", self.html)
        self.assertIn("data/site-index.json", self.html)
        self.assertIn("function getSiteIndexPath()", self.html)
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

    def test_ui_surfaces_curation_status(self):
        self.assertHtmlContains("item.curationStatus")
        self.assertHtmlContains("itemStatusText")
        self.assertHtmlContains("status-chip")
        self.assertHtmlContains("kanji-status")
        self.assertHtmlContains("Generated entry")

    def test_ui_prefers_curated_item_for_initial_detail(self):
        self.assertHtmlContains("function getPreferredItem(items)")
        self.assertHtmlContains('item.curationStatus !== "unreviewed"')

    def test_pages_entrypoint_links_to_design_ui_with_relative_path(self):
        entrypoint_path = Path("index.html")

        self.assertTrue(entrypoint_path.exists())
        entrypoint = entrypoint_path.read_text(encoding="utf-8")

        self.assertIn("design/radical-kanji-ui.html", entrypoint)
        self.assertNotIn("/design/radical-kanji-ui.html", entrypoint)


if __name__ == "__main__":
    unittest.main()
