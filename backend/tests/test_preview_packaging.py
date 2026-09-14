"""Packaging allowlist and pinned payload checks, without building an image."""

import unittest
from pathlib import Path
from unittest.mock import patch

from app.preview_candidate_payload import PUBLIC_ASSETS, validate_candidate_payload
from scripts.prepare_preview_context import BACKEND_FILES, PARCOURS_FILES, inputs


ROOT = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    def test_context_is_exact_allowlist_not_private_or_raw_cache(self):
        with patch.object(Path, "is_file", return_value=True), patch.object(Path, "is_symlink", return_value=False):
            selected = inputs(Path("backend"), Path("cache"), Path("parcours"))
        destinations = [target.as_posix() for _source, target in selected]
        self.assertEqual(len(destinations), len(set(destinations)))
        self.assertEqual(len(destinations), len(BACKEND_FILES) + len(PUBLIC_ASSETS) + len(PARCOURS_FILES))
        self.assertFalse(any(any(part in path for part in (
            "private", "static/", "mapping", ".xlsx", "General", "vectors/", "evaluat", ".log", ".env"))
            for path in destinations))
        self.assertEqual(set(PUBLIC_ASSETS), {
            "snapshot.json", "embeddings.json", "embeddings.npy",
            "tokenizer/fb374d419588a4632f3f557e76b4b70aebbca790"})

    def test_dockerignore_includes_only_declared_files(self):
        allowed = {
            line[1:] for line in (ROOT / "Dockerfile.dev-preview.dockerignore").read_text().splitlines()
            if line.startswith("!") and not line.endswith("/")
        }
        expected = set(BACKEND_FILES) | {"parcours/" + name for name in PARCOURS_FILES}
        expected |= {"public-catalogue/" + name for name in PUBLIC_ASSETS}
        self.assertEqual(allowed, expected)

    def test_final_image_never_inherits_private_base_layers_or_old_entrypoint(self):
        recipe = (ROOT / "Dockerfile.dev-preview").read_text()
        self.assertIn("FROM ${BASE_IMAGE} AS validation", recipe)
        final = recipe.split("FROM scratch", 1)[1]
        self.assertNotIn("COPY --from=validation /app", final)
        self.assertNotIn("COPY --from=validation /root", final)
        self.assertNotIn("entrypoint.sh", final)
        self.assertIn('"app.preview:create_app", "--factory"', final)
        self.assertIn('"--workers", "1"', final)
        self.assertIn('"--no-proxy-headers", "--no-access-log"', final)
        self.assertIn("USER 65532:65532", final)
        self.assertIn('create_app(mode="synthetic")', final)
        self.assertIn("-r requirements-preview.txt", recipe)
        self.assertNotIn("AZURE_OPENAI_API_KEY=", recipe)

    def test_missing_or_modified_public_assets_cannot_start(self):
        with patch.object(Path, "is_file", return_value=False), self.assertRaises(ValueError):
            validate_candidate_payload(Path("unused"))
        with patch.object(Path, "is_file", return_value=True), \
                patch.object(Path, "is_symlink", return_value=False), \
                patch.object(Path, "read_bytes", return_value=b"modified-public-payload"), \
                self.assertRaises(ValueError):
            validate_candidate_payload(Path("unused"))
