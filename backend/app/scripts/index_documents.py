"""
Indexation des documents dans Chroma (même base que l'API).
À lancer avec des chemins en arguments (fichiers ou dossiers).
Exemple : python -m app.scripts.index_documents --clear /data/docs /data/fic.pdf
"""

import argparse
import sys
from pathlib import Path

# Permet d'importer app depuis la racine backend
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.haystack_rag import clear_all_documents, get_document_store, index_documents_haystack
from app.services.ingest import _lc_to_haystack_docs, load_and_split_documents

SUPPORTED_SUFFIXES = (".pdf", ".txt", ".md", ".xlsx")


def collect_files(paths: list[str]) -> list[Path]:
    """Collecte tous les fichiers supportés à partir de chemins (fichiers ou dossiers)."""
    collected: list[Path] = []
    for p in paths:
        path = Path(p).resolve()
        if not path.exists():
            raise ValueError("Une source demandée n'existe pas.")
        if path.is_file():
            if path.suffix.lower() in SUPPORTED_SUFFIXES:
                collected.append(path)
            else:
                raise ValueError("Une source demandée a un type non supporté.")
        else:
            for ext in SUPPORTED_SUFFIXES:
                collected.extend(path.rglob(f"*{ext}"))
    return sorted(set(collected))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Indexe des documents (PDF, TXT, MD, XLSX) dans Chroma (même base que l'API)."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Fichiers ou dossiers à indexer",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--clear",
        action="store_true",
        help="Vider l'index Chroma seulement après validation de toutes les sources",
    )
    mode.add_argument(
        "--validate-only",
        action="store_true",
        help="Lire et valider les sources sans accès à Chroma ni appel embeddings",
    )
    mode.add_argument(
        "--require-empty",
        action="store_true",
        help="Refuser l'écriture si la collection cible n'est pas vide (préparation isolée)",
    )
    args = parser.parse_args(argv)

    files = collect_files(args.paths)
    if not files:
        raise ValueError("Aucun fichier pris en charge à indexer.")

    prepared = []
    for f in files:
        docs = load_and_split_documents(str(f))
        if not docs:
            raise ValueError("Une source ne contient aucun document indexable.")
        prepared.extend(_lc_to_haystack_docs(docs, str(f)))

    print(f"Sources validées : {len(files)} fichier(s), {len(prepared)} document(s).")
    if args.validate_only:
        print("Aucune écriture d'index ni requête embeddings effectuée.")
        return

    if args.require_empty and get_document_store().count_documents() != 0:
        raise ValueError("La collection cible n'est pas vide ; choisir une collection isolée.")
    # No destructive operation occurs until every input has been loaded successfully.
    if args.clear:
        print("Vidage de l'index Chroma après validation des sources…")
        clear_all_documents()

    count = index_documents_haystack(prepared)
    if count != len(prepared):
        raise RuntimeError("Le nombre de documents indexés ne correspond pas aux sources préparées.")
    print(f"Indexation terminée : {count} document(s).")


if __name__ == "__main__":
    main()
