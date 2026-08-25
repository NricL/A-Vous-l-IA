import unittest
from unittest.mock import patch

from app import haystack_rag


class FakeRetrievalPipeline:
    def __init__(self, documents):
        self._documents = documents

    def run(self, payload):
        self.payload = payload
        return {"retriever": {"documents": self._documents}}


class HaystackRagRetrievalFilterTests(unittest.TestCase):
    def test_build_pool_does_not_mix_triggers_when_intention_has_no_match(self):
        class _Doc:
            def __init__(self, intention, trigger):
                self.meta = {
                    "intention": intention,
                    "declencheurs_typiques": trigger,
                }

        docs = [
            _Doc("Analyser la performance marketing", "analyse manuelle longue"),
            _Doc("Créer des contenus marketing", "charge rédactionnelle élevée"),
        ]
        with patch.object(haystack_rag, "_fetch_documents_for_domaine", return_value=docs):
            triggers = haystack_rag.build_pool(
                "marketing_visibilite",
                intention="Intention absente",
            )

        self.assertEqual(triggers, [])

    def test_build_pool_filters_triggers_by_selected_intention(self):
        class _Doc:
            def __init__(self, intention, trigger):
                self.meta = {
                    "intention": intention,
                    "declencheurs_typiques": trigger,
                }

        docs = [
            _Doc("Analyser la performance marketing", "analyse manuelle longue"),
            _Doc("Créer des contenus marketing", "charge rédactionnelle élevée"),
        ]
        with patch.object(haystack_rag, "_fetch_documents_for_domaine", return_value=docs):
            triggers = haystack_rag.build_pool(
                "marketing_visibilite",
                intention="Créer des contenus marketing",
            )

        self.assertEqual(triggers, ["charge rédactionnelle élevée"])

    def test_build_retrieval_filters_combines_domain_and_intention_metadata(self):
        with patch.object(
            haystack_rag,
            "_get_intention_label_from_code",
            return_value="Structurer un reporting fiable",
        ):
            filters = haystack_rag._build_retrieval_filters(
                domaine_code="finance_pilotage",
                intention_code="2",
            )

        self.assertIsNotNone(filters)
        self.assertEqual(filters["operator"], "AND")
        self.assertEqual(len(filters["conditions"]), 2)

        domain_filter, intention_filter = filters["conditions"]
        self.assertEqual(domain_filter["operator"], "OR")
        self.assertEqual(intention_filter["operator"], "OR")

        domain_values = {condition["value"] for condition in domain_filter["conditions"]}
        self.assertIn("finance_pilotage", domain_values)
        self.assertIn("Finances & rentabilité", domain_values)

        intention_values = {condition["value"] for condition in intention_filter["conditions"]}
        self.assertEqual(intention_values, {"Structurer un reporting fiable"})

    def test_retrieve_docs_for_question_applies_metadata_filters_before_retrieval(self):
        captured = {}
        fake_pipeline = FakeRetrievalPipeline(documents=[["doc-a", "doc-b"]])

        def fake_build_pipeline(filters=None):
            captured["filters"] = filters
            return fake_pipeline

        with (
            patch.object(haystack_rag, "_get_intention_label_from_code", return_value="Structurer un reporting fiable"),
            patch.object(haystack_rag, "build_rag_retrieval_only_pipeline", side_effect=fake_build_pipeline),
        ):
            docs = haystack_rag._retrieve_docs_for_question(
                "rapport solide et comprehensible",
                selected_domain_code="finance_pilotage",
                selected_intention="2",
            )

        self.assertEqual(docs, ["doc-a", "doc-b"])
        self.assertEqual(fake_pipeline.payload, {"embedder": {"text": "rapport solide et comprehensible"}})

        filters = captured["filters"]
        self.assertIsNotNone(filters)
        self.assertEqual(filters["operator"], "AND")

        domain_filter, intention_filter = filters["conditions"]
        domain_values = {condition["value"] for condition in domain_filter["conditions"]}
        intention_values = {condition["value"] for condition in intention_filter["conditions"]}

        self.assertIn("finance_pilotage", domain_values)
        self.assertIn("Finances & rentabilité", domain_values)
        self.assertEqual(intention_values, {"Structurer un reporting fiable"})

    def test_retrieve_docs_for_question_never_drops_intention_when_sector_has_few_matches(self):
        """
        Régression : si moins de 3 documents matchent domaine+intention+secteur,
        le fallback ne doit JAMAIS relâcher l'intention (sinon des cas d'une
        autre intention sont proposés pour compléter le quota, ex. bug
        marketing où 'Lancement de produit' apparaissait sous l'intention
        'Créer des contenus marketing').
        """
        calls = []

        # Étape 1 (domaine+intention+secteur) ne renvoie qu'1 doc réel.
        # Le prochain appel de fallback doit garder l'intention (secteur+multisectoriel),
        # jamais un appel avec intention_code=None alors qu'une intention est sélectionnée.
        responses = [
            [{"id": "only-real-match"}],  # étape 1: 1 seul doc réel pour l'intention choisie
        ]

        def fake_build_pipeline(filters=None):
            calls.append(filters)
            docs = responses[0] if len(calls) == 1 else []
            return FakeRetrievalPipeline(documents=docs)

        with (
            patch.object(haystack_rag, "_get_intention_label_from_code", return_value="Créer des contenus marketing"),
            patch.object(haystack_rag, "build_rag_retrieval_only_pipeline", side_effect=fake_build_pipeline),
        ):
            docs = haystack_rag._retrieve_docs_for_question(
                "je perds du temps à créer des fiches produit",
                selected_domain_code="marketing_visibilite",
                selected_intention="3",
                selected_sector="Commerce & retail",
            )

        # Le fallback s'arrête dès qu'il y a au moins 1 doc réel (pas de padding).
        self.assertEqual(docs, [{"id": "only-real-match"}])

        # Aucun des appels de filtre effectués n'a droppé l'intention alors
        # qu'une intention était sélectionnée.
        def _contains_intention_field(node) -> bool:
            field = node.get("field")
            if field and field.rsplit(".", 1)[-1] in haystack_rag.INTENTION_META_KEYS:
                return True
            return any(_contains_intention_field(sub) for sub in node.get("conditions", []))

        for filt in calls:
            self.assertIsNotNone(filt)
            self.assertTrue(
                _contains_intention_field(filt),
                f"Le filtre {filt!r} a relâché l'intention alors qu'une intention était sélectionnée.",
            )


class HaystackRagCaseExtraFieldsTests(unittest.TestCase):
    def test_doc_to_case_dict_reads_canonical_and_alias_headers(self):
        class _Doc:
            id = "row-1"
            content = "Texte RAG"
            meta = {
                "effort": "Moyen",
                "prerequis_donnees": "Export CSV",
                "Guardrails": "Vérifier sources",
                "questions_qualification": "Q1 ?\nQ2 ?",
                "data_sensitivity": "Données perso",
            }

        row = haystack_rag._doc_to_case_dict(_Doc(), 0)
        self.assertEqual(row["id"], "row-1")
        self.assertEqual(row["content"], "Texte RAG")
        self.assertEqual(row["effort"], "Moyen")
        self.assertEqual(row["prerequis_donnees"], "Export CSV")
        self.assertEqual(row["guardrails"], "Vérifier sources")
        self.assertEqual(row["questions_qualification"], "Q1 ?\nQ2 ?")
        self.assertEqual(row["sensibilite_donnees"], "Données perso")

    def test_docs_to_payload_aligns_extras_with_contents(self):
        class _Doc:
            def __init__(self, mid, text, meta):
                self.id = mid
                self.content = text
                self.meta = meta

        docs = [
            _Doc("a", "c1", {"effort": "Faible"}),
            _Doc("b", "c2", {}),
        ]
        _s, ids, contents, extras = haystack_rag._docs_to_payload(docs)
        self.assertEqual(ids, ["a", "b"])
        self.assertEqual(contents, ["c1", "c2"])
        self.assertEqual(extras[0]["effort"], "Faible")
        self.assertIsNone(extras[1]["effort"])

    def test_doc_to_case_dict_prefers_uc_business_id_from_explicit_meta_key(self):
        class _Doc:
            id = "7e8f9a10b11c12d1"
            content = "Texte RAG"
            meta = {
                "case_id": "UC-0059",
                "effort": "Faible",
            }

        row = haystack_rag._doc_to_case_dict(_Doc(), 0)
        self.assertEqual(row["id"], "UC-0059")
        self.assertEqual(row["effort"], "Faible")

    def test_doc_to_case_dict_finds_uc_business_id_in_freeform_meta_values(self):
        class _Doc:
            id = "7e8f9a10b11c12d1"
            content = "Texte RAG"
            meta = {
                "cas_utilisation": "UC-0170 — Réponses standard retard livraison",
            }

        row = haystack_rag._doc_to_case_dict(_Doc(), 0)
        self.assertEqual(row["id"], "UC-0170")


if __name__ == "__main__":
    unittest.main()
