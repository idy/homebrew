import copy
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import update_casks as updater


def release(project, version="1.2.3"):
    return {
        "tag_name": f"v{version}",
        "draft": False,
        "prerelease": False,
        "assets": [
            {
                "name": pattern.format(version=version),
                "browser_download_url": (
                    f"https://github.com/idy/{project}/releases/download/v{version}/"
                    + pattern.format(version=version)
                ),
                "digest": "sha256:" + str(index + 1) * 64,
            }
            for index, pattern in enumerate(updater.ASSETS[project].values())
        ],
    }


def cask(project):
    content = (updater.ROOT / "Casks" / f"{project}.rb").read_text()
    # Keep fixtures independent of whichever version is currently published.
    return re.sub(r'^  version "[^"]+"$', '  version "1.0.0"', content, flags=re.MULTILINE)


class UpdateCasksTests(unittest.TestCase):
    def test_updates_both_architectures_and_is_idempotent(self):
        candidate = release("tailsplit")
        updated = updater.update_content("tailsplit", cask("tailsplit"), candidate)
        self.assertIn('version "1.2.3"', updated)
        self.assertIn('arm:   "' + "1" * 64 + '"', updated)
        self.assertIn('intel: "' + "2" * 64 + '"', updated)
        self.assertEqual(updated, updater.update_content("tailsplit", updated, candidate))

    def test_rejects_incomplete_multi_architecture_release(self):
        candidate = release("tailsplit")
        candidate["assets"].pop()
        with self.assertRaisesRegex(ValueError, "expected exactly one"):
            updater.release_values("tailsplit", candidate)

    def test_rejects_drafts_prereleases_and_unsafe_tags(self):
        for changes in ({"draft": True}, {"prerelease": True}, {"tag_name": 'v1.2.3#{evil}'}):
            with self.subTest(changes=changes):
                candidate = release("nootify") | changes
                with self.assertRaises(ValueError):
                    updater.release_values("nootify", candidate)

    def test_rejects_missing_or_invalid_asset_checksums(self):
        for digest in (None, "sha256:short", "sha512:" + "1" * 64):
            with self.subTest(digest=digest):
                candidate = release("nootify")
                candidate["assets"][0]["digest"] = digest
                with self.assertRaisesRegex(ValueError, "missing SHA-256"):
                    updater.release_values("nootify", candidate)

    def test_rejects_unexpected_asset_urls_and_duplicates(self):
        candidate = release("nootify")
        candidate["assets"][0]["browser_download_url"] = "https://example.com/Nootify.dmg"
        with self.assertRaisesRegex(ValueError, "unexpected download URL"):
            updater.release_values("nootify", candidate)
        candidate = release("nootify")
        candidate["assets"].append(copy.deepcopy(candidate["assets"][0]))
        with self.assertRaisesRegex(ValueError, "expected exactly one"):
            updater.release_values("nootify", candidate)

    def test_refuses_downgrades_and_replaced_release_assets(self):
        updated = updater.update_content("nootify", cask("nootify"), release("nootify"))
        with self.assertRaisesRegex(ValueError, "refusing downgrade"):
            updater.update_content("nootify", updated, release("nootify", "1.2.2"))
        replaced = release("nootify")
        replaced["assets"][0]["digest"] = "sha256:" + "9" * 64
        with self.assertRaisesRegex(ValueError, "changed checksums"):
            updater.update_content("nootify", updated, replaced)

    def test_invalid_second_release_leaves_every_cask_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Casks").mkdir()
            for project in updater.ASSETS:
                (root / "Casks" / f"{project}.rb").write_text(cask(project))
            broken = release("nootify")
            broken["assets"] = []
            with patch.object(updater, "latest_release", side_effect=[release("tailsplit"), broken]):
                with self.assertRaises(ValueError):
                    updater.update_projects(list(updater.ASSETS), root=root)
            for project in updater.ASSETS:
                self.assertEqual(cask(project), (root / "Casks" / f"{project}.rb").read_text())

    def test_check_mode_reports_updates_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Casks").mkdir()
            path = root / "Casks" / "nootify.rb"
            path.write_text(cask("nootify"))
            with patch.object(updater, "latest_release", return_value=release("nootify")):
                self.assertTrue(updater.update_projects(["nootify"], check=True, root=root))
            self.assertEqual(cask("nootify"), path.read_text())


if __name__ == "__main__":
    unittest.main()
