from pathlib import Path
import tempfile
import unittest

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.testclient import TestClient

from app.parcours_static import ParcoursStaticFiles


class PrivateExportServingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for filename in (
            "index.html", "action-synthetic01.html", "style.css", "app.js", "robots.txt",
            "mapping_uc_hash.csv", "MAPPING.CSV", "source.xlsx", "source.xlsm",
            "audit.json", "audit.txt", "notes.md", ".env",
        ):
            (self.root / filename).write_text("synthetic-content", encoding="utf-8")
        self.app = Starlette(routes=[Mount("/", app=ParcoursStaticFiles(directory=self.root, html=True))])
        self.client = self.enterContext(TestClient(self.app))

    def test_pages_and_assets_remain_available(self):
        for path in ("/", "/action-synthetic01.html", "/style.css", "/app.js", "/robots.txt"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.text, "synthetic-content")

    def test_sources_and_mapping_are_never_served(self):
        for path in (
            "/mapping_uc_hash.csv", "/MAPPING.CSV", "/mapping_uc_hash%2ecsv",
            "/source.xlsx", "/source.xlsm", "/audit.json", "/audit.txt", "/notes.md", "/.env",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 404)
                self.assertNotIn("synthetic-content", response.text)

    def test_hidden_directories_do_not_expose_html(self):
        (self.root / ".private").mkdir()
        (self.root / ".private" / "hidden.html").write_text("private-synthetic")
        self.assertEqual(self.client.get("/.private/hidden.html").status_code, 404)

    def test_legacy_hash_directory_still_serves_its_index(self):
        directory = self.root / "action" / "synthetic01"
        directory.mkdir(parents=True)
        (directory / "index.html").write_text("synthetic-page")
        self.assertEqual(self.client.get("/action/synthetic01/").text, "synthetic-page")

    def test_parent_traversal_is_rejected(self):
        self.assertEqual(self.client.get("/%2e%2e/private.html").status_code, 404)


if __name__ == "__main__":
    unittest.main()
