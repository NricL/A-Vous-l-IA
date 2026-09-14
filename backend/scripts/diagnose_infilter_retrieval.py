"""Opt-in, read-only deployed-index diagnosis; emits IDs/counts, never source text.

Run with python -B. This does not initialize Chroma, run embeddings, call a model,
or write a report. Vector order is unknown: the target's lexical rank interval
accounts for every possible vector tie order. It is not an HTTP trace.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import sqlite3
import sys
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import haystack_rag as rag


def matches_filter(doc, node):
    if not node:
        return True
    if "conditions" in node:
        combine = all if node["operator"] == "AND" else any
        return combine(matches_filter(doc, child) for child in node["conditions"])
    if node["operator"] != "==":
        raise ValueError("Unsupported diagnostic filter operator")
    return doc.meta.get(node["field"].removeprefix("meta.")) == node["value"]


def read_documents():
    settings = rag.get_settings()
    path = (Path(settings.chroma_persist_dir) / "chroma.sqlite3").resolve()
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as connection:
        collection = connection.execute(
            "SELECT id FROM collections WHERE name = ?", (settings.chroma_collection_name,),
        ).fetchone()
        if not collection:
            raise ValueError("Configured collection is absent")
        segment = connection.execute(
            "SELECT id FROM segments WHERE collection = ? AND scope = 'METADATA'", collection,
        ).fetchone()
        if not segment:
            raise ValueError("Configured metadata segment is absent")
        metadata = defaultdict(dict)
        for identifier, key, string, integer, number, boolean in connection.execute(
            "SELECT m.id, m.key, m.string_value, m.int_value, m.float_value, m.bool_value "
            "FROM embedding_metadata m JOIN embeddings e ON e.id = m.id WHERE e.segment_id = ?",
            segment,
        ):
            metadata[identifier][key] = next(
                (value for value in (string, integer, number, boolean) if value is not None), None,
            )
        return [
            SimpleNamespace(
                id=identifier, content=metadata[key].pop("chroma:document", ""), meta=metadata[key],
            )
            for key, identifier in connection.execute(
                "SELECT id, embedding_id FROM embeddings WHERE segment_id = ? ORDER BY id", segment,
            )
        ]


def diagnose(query, domain, sector, intention, case_id=None):
    documents = read_documents()

    def domain_documents(code, **kwargs):
        return [doc for doc in documents if rag._doc_matches_domain(doc, rag._get_domaine_label(code), code)]

    def identifier(doc):
        return rag._extract_case_id_from_meta(doc.meta) or doc.id

    stages = []
    with patch.object(rag, "_fetch_documents_for_domaine", side_effect=domain_documents):
        if not rag._get_intention_label_from_code(domain, intention, secteur_choisi=sector):
            raise ValueError("Selected intention is invalid")
        for include_multisector in (False, True):
            filters = rag._build_retrieval_filters(domain, intention, sector, include_multisector)
            eligible = [doc for doc in documents if matches_filter(doc, filters)]
            ranked = rag._rank_docs_by_query_overlap(query, eligible)
            target = next((doc for doc in eligible if identifier(doc) == case_id), None)
            stage = {
                "include_multisector": include_multisector,
                "eligible_count": len(eligible),
                "eligible_ids": [identifier(doc) for doc in eligible],
                "lexical_ids_database_tie_order": [identifier(doc) for doc in ranked],
                "target_present": target is not None,
            }
            if target:
                higher, tied = [], []
                for other in eligible:
                    if other is target:
                        continue
                    if rag._rank_docs_by_query_overlap(query, [target, other])[0] is other:
                        higher.append(identifier(other))
                    elif rag._rank_docs_by_query_overlap(query, [other, target])[0] is other:
                        tied.append(identifier(other))
                stage["strictly_higher_lexical_ids"] = higher
                stage["tied_lexical_ids"] = tied
                stage["target_rank_interval_any_vector_tie_order"] = [
                    len(higher) + 1, len(higher) + len(tied) + 1,
                ]
            if eligible and len(eligible) <= rag.get_settings().top_k_retrieve:
                prompt = rag._build_rag_prompt_from_docs(
                    query, "", "", ranked, [{"role": "user", "content": query}],
                    selected_domain_code=domain, selected_sector=sector, selected_intention=intention,
                )
                candidates = json.loads(prompt.rsplit("\n\n", 1)[1])["candidats"]
                target_number = next((i for i, doc in enumerate(ranked, 1) if doc is target), None)
                stage["prompt_candidate_count_database_tie_order"] = len(candidates)
                stage["target_in_prompt_database_tie_order"] = any(
                    row["numero"] == target_number for row in candidates
                )
            stages.append(stage)
            if eligible:
                break
    return {
        "mode": "read_only_metadata_and_production_reranking_not_http_trace",
        "top_k_retrieve": rag.get_settings().top_k_retrieve,
        "index_document_count": len(documents),
        "domain_document_count": len(domain_documents(domain)),
        "stages": stages,
        "model_called": False,
        "source_text_exported": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-index", action="store_true", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--domain", required=True)
    parser.add_argument("--sector", required=True)
    parser.add_argument("--intention", required=True)
    parser.add_argument("--case-id")
    args = parser.parse_args()
    print(json.dumps(diagnose(args.query, args.domain, args.sector, args.intention, args.case_id)))


if __name__ == "__main__":
    main()
