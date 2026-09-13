import csv
import json
from pathlib import Path
import tempfile
import unittest

from openpyxl import Workbook

from app.scripts.validate_release_payload import quarantine_static_exports, sha256, validate_payload


class ReleasePayloadTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source.xlsx"
        book = Workbook()
        book.active.title = "Sheet1"
        book.active.append(["use_case_id", "rag_text_auto"])
        book.active.append(["SYN-01", "Synthetic source"])
        book.save(self.source)
        book.close()
        self.mapping = self.root / "mapping.csv"
        with self.mapping.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["case_id", "case_hash"])
            writer.writerows([["SYN-01", "synthetic01"], ["OLD-01", "synthetic02"]])
        self.pages = self.root / "pages"
        self.pages.mkdir()
        for name in ("action-synthetic01.html", "action-synthetic02.html"):
            (self.pages / name).write_text("Synthetic page", encoding="utf-8")
        self.manifest = self.root / "manifest.json"
        self.payload = {
            "workbook_sha256": sha256(self.source), "mapping_sha256": sha256(self.mapping),
            "case_count": 1,
            "pages": {"action-synthetic01.html": sha256(self.pages / "action-synthetic01.html")},
            "historical_pages": {"action-synthetic02.html": sha256(self.pages / "action-synthetic02.html")},
        }

    def validate(self):
        self.manifest.write_text(json.dumps(self.payload), encoding="utf-8")
        return validate_payload(self.source, self.mapping, self.manifest, self.pages)

    def test_complete_payload_preserves_old_pages(self):
        self.assertEqual(self.validate(), {"cases": 1, "current_pages": 1, "historical_pages_preserved": 1})

    def test_private_mapping_in_webroot_fails(self):
        (self.pages / "mapping_uc_hash.csv").write_text("private")
        with self.assertRaisesRegex(ValueError, "Private source"):
            self.validate()

    def test_wrong_source_and_mapping_hashes_fail(self):
        for field in ("workbook_sha256", "mapping_sha256"):
            with self.subTest(field=field):
                previous = self.payload[field]
                self.payload[field] = "wrong"
                with self.assertRaises(ValueError):
                    self.validate()
                self.payload[field] = previous

    def test_wrong_count_and_page_set_fail(self):
        self.payload["case_count"] = 2
        with self.assertRaises(ValueError):
            self.validate()
        self.payload["case_count"] = 1
        self.payload["pages"] = {}
        with self.assertRaises(ValueError):
            self.validate()

    def test_modified_historical_page_fails(self):
        (self.pages / "action-synthetic02.html").write_text("changed")
        with self.assertRaisesRegex(ValueError, "historical_pages"):
            self.validate()

    def test_unsafe_manifest_path_fails(self):
        self.payload["historical_pages"] = {"../escape.html": "anything"}
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            self.validate()

    def test_inherited_exports_are_preserved_outside_webroot(self):
        nested = self.pages / "legacy"
        nested.mkdir()
        for name in ("mapping.csv", "source.XLSX", "audit.json", "notes.md", "review.txt"):
            (nested / name).write_text("synthetic-private")
        (self.pages / "robots.txt").write_text("User-agent: *")
        private = self.root / "private"
        self.assertEqual(quarantine_static_exports(self.pages, private), 5)
        self.assertTrue((self.pages / "robots.txt").is_file())
        self.assertEqual((private / "legacy" / "source.XLSX").read_text(), "synthetic-private")
        self.assertEqual(self.validate()["current_pages"], 1)
        self.assertEqual(quarantine_static_exports(self.pages, private), 0)

    def test_quarantine_does_not_overwrite_existing_private_copy(self):
        (self.pages / "mapping.csv").write_text("new")
        private = self.root / "private"
        private.mkdir()
        (private / "mapping.csv").write_text("old")
        with self.assertRaisesRegex(ValueError, "already exists"):
            quarantine_static_exports(self.pages, private)
        self.assertEqual((self.pages / "mapping.csv").read_text(), "new")
        self.assertEqual((private / "mapping.csv").read_text(), "old")


if __name__ == "__main__":
    unittest.main()
