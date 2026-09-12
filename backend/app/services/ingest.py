"""
Ingestion de documents : chargement, découpage, ajout au vector store (Chroma via Haystack).
Pour les XLSX : indexation par ligne (1 ligne = 1 chunk), contenu = colonne rag_text_auto, reste en métadonnées.
"""

from __future__ import annotations

from pathlib import Path
from contextlib import ExitStack
from typing import TYPE_CHECKING

from openpyxl import load_workbook

from app.rag_constants import CASE_EXTRA_FIELD_ALIASES, DOMAINE_META_KEYS, INTENTION_META_KEYS

if TYPE_CHECKING:
    from langchain_core.documents import Document as LangChainDocument
    from haystack import Document as HaystackDocument

# Colonne dont la valeur est vectorisée ; les autres colonnes vont en métadonnées.
RAG_TEXT_AUTO_COLUMN = "rag_text_auto"
CATALOGUE_REQUIRED = {"use_case_id", RAG_TEXT_AUTO_COLUMN}
# Explicit business fields prevent audit/review columns becoming retrieval context.
CATALOGUE_METADATA = (
    {"use_case_id", "domaine_code", "micro_theme"}
    | set(DOMAINE_META_KEYS) | set(INTENTION_META_KEYS)
    | {alias for aliases in CASE_EXTRA_FIELD_ALIASES.values() for alias in aliases}
)


def _cell_str(value) -> str:
    """Convertit une cellule en chaîne pour contenu ou métadonnées."""
    if value is None:
        return ""
    return str(value).strip()


def _load_xlsx(file_path: str) -> list[LangChainDocument]:
    """Read Sheet1, or one unambiguous legacy catalogue; never serve audit sheets."""
    from langchain_core.documents import Document as LangChainDocument
    with ExitStack() as stack:
        wb = load_workbook(file_path, read_only=True, data_only=True)
        stack.callback(wb.close)
        raw = load_workbook(file_path, read_only=True, data_only=False)
        stack.callback(raw.close)
        if "Sheet1" in wb.sheetnames:
            sheet = wb["Sheet1"]
        else:
            candidates = [
                sheet for sheet in wb.worksheets
                if sheet.title.upper() != "BASE_PROPOSEE"
                and CATALOGUE_REQUIRED <= {
                    _cell_str(c.value) for c in next(sheet.iter_rows(), ())
                }
            ]
            if len(candidates) != 1:
                raise ValueError("Catalogue sheet missing or ambiguous; expected Sheet1.")
            sheet = candidates[0]
        rows = sheet.iter_rows()
        headers = [_cell_str(c.value) for c in next(rows, ())]
        named = [h for h in headers if h]
        if len(named) != len(set(named)):
            raise ValueError("Duplicate catalogue headers.")
        if not CATALOGUE_REQUIRED <= set(headers):
            raise ValueError("Required catalogue headers missing.")
        raw_rows = raw[sheet.title].iter_rows()
        if any(c.data_type in ("e", "f") for c in next(raw_rows, ())):
            raise ValueError("Invalid catalogue header cells.")
        served = CATALOGUE_METADATA | {RAG_TEXT_AUTO_COLUMN}
        docs, seen = [], set()
        for row_idx, (row, source_row) in enumerate(zip(rows, raw_rows), start=2):
            if all(c.value is None and c.data_type not in ("s", "inlineStr", "f", "e") for c in source_row):
                continue
            values = {}
            for header, cell, source_cell in zip(headers, row, source_row):
                if not header and source_cell.value is not None:
                    raise ValueError(f"Unnamed populated column at row {row_idx}.")
                if header not in served:
                    continue
                if cell.data_type == "e" or source_cell.data_type == "e":
                    raise ValueError(f"Excel error in served cell at row {row_idx}.")
                if source_cell.data_type == "f" and cell.value is None:
                    raise ValueError(f"Missing formula cache at row {row_idx}.")
                values[header] = _cell_str(cell.value)
            uc, content = values.get("use_case_id", ""), values.get(RAG_TEXT_AUTO_COLUMN, "")
            if not uc or not content:
                raise ValueError(f"Blank catalogue ID or RAG content at row {row_idx}.")
            if uc.upper() in seen:
                raise ValueError(f"Duplicate catalogue ID at row {row_idx}.")
            seen.add(uc.upper())
            meta = {k: v for k, v in values.items() if k != RAG_TEXT_AUTO_COLUMN}
            meta.update(source_file=Path(file_path).name, sheet=sheet.title, row_index=row_idx)
            docs.append(LangChainDocument(page_content=content, metadata=meta))
        return docs


def get_loader_for_path(file_path: str):
    """Retourne le loader LangChain adapté au type de fichier (ou None pour xlsx, géré à part)."""
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        from langchain_community.document_loaders import PyPDFLoader
        return PyPDFLoader(file_path)
    if suffix in (".txt", ".md"):
        from langchain_community.document_loaders import TextLoader
        return TextLoader(file_path, encoding="utf-8")
    if suffix == ".xlsx":
        return None  # géré par load_and_split_documents
    raise ValueError(f"Type de fichier non supporté : {suffix}")


def load_and_split_documents(file_path: str) -> list[LangChainDocument]:
    """Charge un fichier et le découpe en chunks (documents LangChain). XLSX : 1 ligne = 1 doc, pas de découpage."""
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        return _load_xlsx(file_path)
    from app.config import get_settings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    settings = get_settings()
    loader = get_loader_for_path(file_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
    )
    return splitter.split_documents(docs)


def _lc_to_haystack_docs(lc_docs: list[LangChainDocument], file_path: str, metadata: dict | None = None) -> list[HaystackDocument]:
    """Convertit des documents LangChain en documents Haystack."""
    from haystack import Document as HaystackDocument
    out = []
    for d in lc_docs:
        meta = dict(d.metadata or {})
        meta["source_file"] = str(Path(file_path).name)
        if metadata:
            meta.update(metadata)
        out.append(HaystackDocument(content=d.page_content, meta=meta))
    return out


def ingest_file(file_path: str, metadata: dict | None = None) -> list[str]:
    """
    Ingère un fichier dans Chroma via Haystack (embedding + écriture).
    Retourne une liste d'ids factices pour compatibilité API (count = len(ids)).
    """
    docs = load_and_split_documents(file_path)
    if not docs:
        return []
    for d in docs:
        d.metadata = d.metadata or {}
        d.metadata["source_file"] = str(Path(file_path).name)
        if metadata:
            d.metadata.update(metadata)
    haystack_docs = _lc_to_haystack_docs(docs, file_path, metadata)
    from app.haystack_rag import index_documents_haystack
    count = index_documents_haystack(haystack_docs)
    return [str(i) for i in range(count)]


def ingest_bytes(content: bytes, filename: str, metadata: dict | None = None) -> list[str]:
    """
    Ingère du contenu binaire (upload) dans Chroma.
    Écrit temporairement sur disque pour les loaders qui lisent des fichiers.
    """
    import tempfile
    suffix = Path(filename).suffix.lower()
    if suffix not in (".pdf", ".txt", ".md", ".xlsx"):
        raise ValueError(f"Type non supporté : {suffix}. Utilisez .pdf, .txt, .md ou .xlsx")
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(content)
        path = f.name
    try:
        return ingest_file(path, metadata=metadata or {"filename": filename})
    finally:
        Path(path).unlink(missing_ok=True)
