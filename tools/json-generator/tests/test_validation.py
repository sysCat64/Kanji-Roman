import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from kanji_roman_generator.validation import validate_project


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def valid_site_index():
    return {
        "schemaVersion": "0.1",
        "defaultRadical": "fish",
        "radicals": [
            {
                "id": "fish",
                "glyph": "魚",
                "labelJa": "魚へん",
                "labelEn": "Fish radical",
                "file": "radicals/fish.json",
                "theme": {
                    "accent": "#0f766e",
                    "accentRgb": "15 118 110",
                    "darkAccent": "#5eead4",
                    "darkAccentRgb": "94 234 212",
                },
            }
        ],
    }


def valid_fish_json():
    return {
        "schemaVersion": "0.1",
        "id": "fish",
        "glyph": "魚",
        "title": "魚へんの漢字",
        "copy": "辞書上の部首が魚に分類されるJIS第一・第二水準の漢字。",
        "tags": ["fish", "spring"],
        "items": [
            {
                "char": "鮭",
                "name": "",
                "meaning": "",
                "readings": {"ja": [], "romaji": []},
                "unicode": "U+9BAD",
                "jis": {"level": 1, "kuten": "26-90"},
                "parts": {"ja": "", "en": ""},
                "note": "",
                "tags": [],
                "curationStatus": "unreviewed",
            },
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
            },
        ],
    }


class ProjectValidationTest(unittest.TestCase):
    def test_validates_public_site_json_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_json(root / "data" / "site-index.json", valid_site_index())
            write_json(root / "data" / "radicals" / "fish.json", valid_fish_json())

            issues = validate_project(root)

        self.assertEqual([], issues)

    def test_reports_public_site_json_contract_violations(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            site_index = valid_site_index()
            site_index["radicals"].append(dict(site_index["radicals"][0]))
            site_index["radicals"][0]["file"] = "/data/radicals/fish.json"
            fish = valid_fish_json()
            fish["tags"].append("All")
            fish["items"][0]["unicode"] = "U+0000"
            fish["items"][0]["jis"]["level"] = 3
            fish["items"][1]["char"] = "鮭"
            fish["items"][1]["tags"] = ["All"]
            write_json(root / "data" / "site-index.json", site_index)
            write_json(root / "data" / "radicals" / "fish.json", fish)

            issues = validate_project(root)

        joined = "\n".join(issues)
        self.assertIn("duplicate radical id: fish", joined)
        self.assertIn("root-relative file path", joined)
        self.assertIn("includes forbidden tag 'All'", joined)
        self.assertIn("unicode mismatch", joined)
        self.assertIn("invalid jis.level", joined)
        self.assertIn("duplicate chars", joined)

    def test_reports_missing_required_public_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            site_index = valid_site_index()
            del site_index["defaultRadical"]
            fish = valid_fish_json()
            del fish["title"]
            del fish["items"][0]["unicode"]
            write_json(root / "data" / "site-index.json", site_index)
            write_json(root / "data" / "radicals" / "fish.json", fish)

            issues = validate_project(root)

        joined = "\n".join(issues)
        self.assertIn("data/site-index.json missing keys: defaultRadical", joined)
        self.assertIn("data/radicals/fish.json missing keys: title", joined)
        self.assertIn("item 0 missing keys: unicode", joined)

    def test_reports_invalid_json_syntax(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / "data" / "site-index.json"
            path.parent.mkdir(parents=True)
            path.write_text("{", encoding="utf-8")

            issues = validate_project(root)

        self.assertEqual(1, len(issues))
        self.assertIn("Invalid JSON in data/site-index.json", issues[0])


class HookValidationTest(unittest.TestCase):
    def test_preflight_uses_generator_validation_module(self):
        script = Path("hooks/validate-project.sh").read_text(encoding="utf-8")

        self.assertIn("kanji_roman_generator.validation", script)

    def test_preflight_rejects_unicode_mismatch(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_json(root / "data" / "site-index.json", valid_site_index())
            fish = valid_fish_json()
            fish["items"][0]["unicode"] = "U+0000"
            write_json(root / "data" / "radicals" / "fish.json", fish)

            result = subprocess.run(
                ["bash", str(Path.cwd() / "hooks" / "validate-project.sh"), str(root)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("unicode mismatch", result.stderr)

    def test_preflight_allows_relative_data_paths_from_design_html(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_json(root / "data" / "site-index.json", valid_site_index())
            write_json(root / "data" / "radicals" / "fish.json", valid_fish_json())
            html_path = root / "design" / "radical-kanji-ui.html"
            html_path.parent.mkdir(parents=True)
            html_path.write_text(
                '<script>const indexUrl = "../data/site-index.json";</script>',
                encoding="utf-8",
            )

            result = subprocess.run(
                ["bash", str(Path.cwd() / "hooks" / "validate-project.sh"), str(root)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)

    def test_preflight_rejects_root_relative_data_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_json(root / "data" / "site-index.json", valid_site_index())
            write_json(root / "data" / "radicals" / "fish.json", valid_fish_json())
            html_path = root / "design" / "radical-kanji-ui.html"
            html_path.parent.mkdir(parents=True)
            html_path.write_text(
                '<script>const indexUrl = "/data/site-index.json";</script>',
                encoding="utf-8",
            )

            result = subprocess.run(
                ["bash", str(Path.cwd() / "hooks" / "validate-project.sh"), str(root)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("root-relative /data/ path found", result.stderr)


class PublicDataFixtureTest(unittest.TestCase):
    def test_public_site_data_contains_planned_radicals(self):
        site_index = json.loads(
            Path("data/site-index.json").read_text(encoding="utf-8")
        )
        radical_ids = [radical["id"] for radical in site_index["radicals"]]

        self.assertEqual(["fish", "grass", "tree", "thread"], radical_ids)
        for radical_id in radical_ids:
            radical_path = Path("data") / "radicals" / f"{radical_id}.json"
            self.assertTrue(
                radical_path.exists(),
                f"Expected public radical JSON at {radical_path}",
            )


if __name__ == "__main__":
    unittest.main()
