import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.scripts import index_documents


class IndexPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "fixture.txt"
        self.source.write_text("Synthetic fixture", encoding="utf-8")
        self.docs = [SimpleNamespace(page_content="Synthetic fixture", metadata={})]
        self.output = io.StringIO()
        self.enterContext(contextlib.redirect_stdout(self.output))
        self.load = self.enterContext(patch.object(index_documents, "load_and_split_documents", return_value=self.docs))
        self.convert = self.enterContext(patch.object(index_documents, "_lc_to_haystack_docs", side_effect=lambda docs, path: docs))
        self.clear = self.enterContext(patch.object(index_documents, "clear_all_documents"))
        self.store = self.enterContext(patch.object(index_documents, "get_document_store"))
        self.index = self.enterContext(patch.object(index_documents, "index_documents_haystack", return_value=1))

    def test_validation_only_never_uses_index_or_embeddings(self):
        index_documents.main(["--validate-only", str(self.source)])
        self.load.assert_called_once_with(str(self.source.resolve()))
        self.clear.assert_not_called()
        self.store.assert_not_called()
        self.index.assert_not_called()
        self.assertNotIn("Synthetic fixture", self.output.getvalue())

    def test_missing_source_prevents_clear(self):
        with self.assertRaises(ValueError):
            index_documents.main(["--clear", str(self.root / "missing.xlsx")])
        self.clear.assert_not_called()
        self.index.assert_not_called()

    def test_empty_directory_prevents_clear(self):
        empty = self.root / "empty"
        empty.mkdir()
        with self.assertRaises(ValueError):
            index_documents.main(["--clear", str(empty)])
        self.clear.assert_not_called()

    def test_unsupported_explicit_input_fails(self):
        other = self.root / "fixture.exe"
        other.write_text("not executable", encoding="utf-8")
        with self.assertRaises(ValueError):
            index_documents.main(["--clear", str(other)])
        self.clear.assert_not_called()

    def test_invalid_later_source_never_clears_or_writes(self):
        second = self.root / "second.xlsx"
        second.touch()
        self.load.side_effect = [self.docs, ValueError("Invalid synthetic catalogue")]
        with self.assertRaises(ValueError):
            index_documents.main(["--clear", str(self.source), str(second)])
        self.clear.assert_not_called()
        self.index.assert_not_called()

    def test_empty_document_source_prevents_clear(self):
        self.load.return_value = []
        with self.assertRaises(ValueError):
            index_documents.main(["--clear", str(self.source)])
        self.clear.assert_not_called()

    def test_require_empty_refuses_existing_collection(self):
        self.store.return_value.count_documents.return_value = 1
        with self.assertRaisesRegex(ValueError, "pas vide"):
            index_documents.main(["--require-empty", str(self.source)])
        self.index.assert_not_called()
        self.clear.assert_not_called()

    def test_clear_occurs_after_loading_and_before_single_write(self):
        events = []
        self.load.side_effect = lambda path: events.append("load") or self.docs
        self.clear.side_effect = lambda: events.append("clear")
        self.index.side_effect = lambda docs: events.append("write") or len(docs)
        index_documents.main(["--clear", str(self.source)])
        self.assertEqual(events, ["load", "clear", "write"])
        self.index.assert_called_once_with(self.docs)

    def test_partial_write_is_not_reported_as_success(self):
        self.index.return_value = 0
        with self.assertRaises(RuntimeError):
            index_documents.main([str(self.source)])
        self.assertNotIn("Indexation terminée", self.output.getvalue())

    def test_require_empty_success_uses_prepared_documents(self):
        self.store.return_value.count_documents.return_value = 0
        index_documents.main(["--require-empty", str(self.source)])
        self.index.assert_called_once_with(self.docs)
        self.clear.assert_not_called()


if __name__ == "__main__":
    unittest.main()
