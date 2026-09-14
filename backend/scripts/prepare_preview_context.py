"""Copy only reviewed preview inputs to a new context, or inspect with --check-only."""

import argparse
import json
import shutil
from pathlib import Path

from app.preview_candidate_payload import PUBLIC_ASSETS
from scripts.validate_preview_candidate import validate

BACKEND_FILES = (
    "Dockerfile.dev-preview", "Dockerfile.dev-preview.dockerignore", "requirements-validation.txt",
    "requirements-preview.txt",
    "app/__init__.py", "app/preview.py", "app/preview_fixture.json", "app/preview_hosting.py",
    "app/preview_candidate_payload.py", "app/preview_parcours.py", "app/preview_protocol.py",
    "app/preview_public_api.py", "app/preview_public_rag.py", "app/preview_publicsnapshot.py",
    "app/preview_repository.py", "app/preview_theme.py", "app/rag_constants.py",
    "scripts/prepare_preview_context.py", "scripts/validate_preview_candidate.py",
    "tests/test_preview_hosting.py", "tests/test_preview_packaging.py", "tests/test_preview_parcours.py",
    "tests/test_preview_protocol.py", "tests/test_preview_public_api.py", "tests/test_preview_public_rag.py",
)
PARCOURS_FILES = (
    "pipeline/genere.py", "templates/page.html.j2",
    "templates/etapes/etape5_outil.md", "templates/etapes/etape5_no_code.md",
    "templates/etapes/etape6_outil.md", "templates/etapes/etape6_no_code.md",
)


def inputs(backend: Path, cache: Path, parcours: Path):
    selected = [(backend / name, Path(name)) for name in BACKEND_FILES]
    selected += [(cache / name, Path("public-catalogue") / name) for name in PUBLIC_ASSETS]
    selected += [(parcours / name, Path("parcours") / name) for name in PARCOURS_FILES]
    for source, _destination in selected:
        if source.is_symlink() or not source.is_file():
            raise ValueError("An explicitly reviewed packaging input is missing or is a symlink.")
    return selected


def prepare(backend: Path, cache: Path, parcours: Path, output: Path | None = None):
    report = validate(cache, parcours)
    selected = inputs(backend, cache, parcours)
    if output is not None:
        output = output.resolve()
        if output.exists() or not output.is_relative_to(Path.cwd().resolve()):
            raise ValueError("Use a new output directory below the current working directory.")
        output.mkdir(parents=True)
        for source, destination in selected:
            target = output / destination
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    return {**report, "files": [destination.as_posix() for _source, destination in selected],
            "context_written": output is not None}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-cache", required=True, type=Path)
    parser.add_argument("--parcours-root", required=True, type=Path)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check-only", action="store_true")
    action.add_argument("--output", type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(Path(__file__).resolve().parents[1], args.public_cache.resolve(),
                             args.parcours_root.resolve(), args.output), ensure_ascii=False, indent=2))
