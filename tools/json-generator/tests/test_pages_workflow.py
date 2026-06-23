import unittest
from pathlib import Path


class GitHubPagesWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.workflow_path = Path(".github/workflows/pages.yml")

    def test_pages_workflow_deploys_curated_static_site_artifact(self):
        self.assertTrue(self.workflow_path.exists())
        workflow = self.workflow_path.read_text(encoding="utf-8")

        self.assertIn("branches: [main]", workflow)
        self.assertIn("PYTHONDONTWRITEBYTECODE=1 bash hooks/preflight.sh", workflow)
        self.assertIn("mkdir -p _site/data _site/design", workflow)
        self.assertIn("cp .nojekyll _site/", workflow)
        self.assertIn("cp design/radical-kanji-ui.html _site/index.html", workflow)
        self.assertIn("cp data/site-index.json _site/data/", workflow)
        self.assertIn("cp -R data/radicals _site/data/", workflow)
        self.assertIn("cp design/radical-kanji-ui.html _site/design/", workflow)
        self.assertIn("uses: actions/configure-pages@v5", workflow)
        self.assertIn("uses: actions/upload-pages-artifact@v4", workflow)
        self.assertIn("path: _site", workflow)
        self.assertIn("include-hidden-files: true", workflow)
        self.assertIn("uses: actions/deploy-pages@v4", workflow)
        self.assertIn("pages: write", workflow)
        self.assertIn("id-token: write", workflow)


if __name__ == "__main__":
    unittest.main()
