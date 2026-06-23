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

    def test_ui_hides_tags_without_matching_items(self):
        self.assertHtmlContains("function visibleTags(collection)")
        self.assertHtmlContains("(item.tags || []).includes(tag)")
        self.assertHtmlContains("const tags = visibleTags(collection)")

    def test_radical_switch_announces_loading_while_previous_list_remains(self):
        select_radical_start = self.html.index("async function selectRadical(radicalId)")
        select_radical_end = self.html.index("async function init()")
        select_radical = self.html[select_radical_start:select_radical_end]

        self.assertIn('resultCount.textContent = "Loading...";', select_radical)
        self.assertIn("if (!getCollection()) renderGrid();", select_radical)

    def test_cached_radical_switch_skips_loading_status(self):
        select_radical_start = self.html.index("async function selectRadical(radicalId)")
        select_radical_end = self.html.index("async function init()")
        select_radical = self.html[select_radical_start:select_radical_end]

        self.assertIn("const hasCachedCollection = Boolean(state.collections[radicalId]);", select_radical)
        self.assertIn("if (!hasCachedCollection) {", select_radical)
        self.assertIn('resultCount.textContent = "Loading...";', select_radical)

    def test_error_messages_do_not_expose_implementation_details(self):
        self.assertNotIn("radical JSON", self.html)
        self.assertNotIn("local HTTP server", self.html)
        self.assertNotIn("data files", self.html)

    def test_page_declares_noop_favicon(self):
        self.assertHtmlContains('rel="icon"')
        self.assertHtmlContains('href="data:,"')

    def test_pages_entrypoint_links_to_design_ui_with_relative_path(self):
        entrypoint_path = Path("index.html")

        self.assertTrue(entrypoint_path.exists())
        entrypoint = entrypoint_path.read_text(encoding="utf-8")

        self.assertIn("design/radical-kanji-ui.html", entrypoint)
        self.assertNotIn("/design/radical-kanji-ui.html", entrypoint)


if __name__ == "__main__":
    unittest.main()
