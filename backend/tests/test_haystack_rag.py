import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app import haystack_rag


class FakeRetrievalPipeline:
    def __init__(self, documents):
        self._documents = documents

    def run(self, payload):
        self.payload = payload
        return {"retriever": {"documents": self._documents}}


class HaystackRagRetrievalFilterTests(unittest.TestCase):
    def setUp(self):
        metadata = patch.object(haystack_rag, "_fetch_documents_for_domaine", return_value=[])
        metadata.start()
        self.addCleanup(metadata.stop)

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

    def test_q3_splits_deduplicates_and_limits_individual_source_examples(self):
        docs = [
            SimpleNamespace(meta={"intention": "Objectif", "secteur": "Cabinet & conseil",
                                  "declencheurs_typiques": f"Échanges   dispersés | Exemple {i} A | Exemple {i} B | Exemple {i} C"})
            for i in range(6)
        ]
        docs += [SimpleNamespace(meta={
            "intention": "Objectif", "secteur": "Cabinet & conseil",
            "Trigger": " echanges disperses | | Exemple 0 A ",
        })]
        source_items = {part.strip() for doc in docs for part in
                        haystack_rag._get_trigger_from_meta(doc.meta).split("|") if part.strip()}
        with patch.object(haystack_rag, "_fetch_documents_for_domaine", return_value=docs):
            pool = haystack_rag.build_pool("relation_client", "Objectif", "Cabinet & conseil")
            self.assertEqual(len(pool), 19)
            self.assertEqual(len({haystack_rag._normalize_query_text(t) for t in pool}), len(pool))
            for accessor in (haystack_rag.get_q3_triggers, haystack_rag._get_triggers_from_store):
                examples = accessor("relation_client", "Objectif", "Cabinet & conseil")
                self.assertEqual(examples, pool[:4])
                self.assertTrue(set(examples) <= source_items)
                self.assertTrue(all("|" not in t for t in examples))

    def test_q3_uses_same_applicability_as_q2_without_padding_other_sectors(self):
        docs = [
            SimpleNamespace(meta={"objectif": "Objectif", "Sector": sector, "situation": trigger})
            for sector, trigger in (
                ("Cabinet et conseil", "Échanges dispersés"),
                ("BTP; Cabinet & conseil", "Réponses incohérentes"),
                ("Multi-sectoriel", "Demande sans réponse"),
                ("Commerce & retail", "Stock commercial"),
                ("Énergie & télécoms", "Consommation énergétique"),
                ("Cabinet & conseil élargi", "Secteur non équivalent"),
                ("", "Secteur absent"),
                ("Autre / Non spécifique", "Secteur non renseigné"),
            )
        ]
        docs += [SimpleNamespace(meta={
            "objectif": "Autre objectif", "Sector": "Cabinet & conseil", "situation": "Facturation",
        })]
        with patch.object(haystack_rag, "_fetch_documents_for_domaine", return_value=docs):
            self.assertEqual(haystack_rag.build_pool(
                "relation_client", "Objectif", "Cabinet & conseil", top_k=6,
            ), ["Échanges dispersés", "Réponses incohérentes", "Demande sans réponse"])
            self.assertEqual(haystack_rag.build_pool(
                "relation_client", "Objectif", "Autre / Non spécifique",
            ), ["Demande sans réponse"])
            self.assertEqual(haystack_rag.build_pool(
                "relation_client", "Autre objectif", "Industrie",
            ), [])
            self.assertIn("Stock commercial", haystack_rag.build_pool("relation_client", "Objectif"))

    def test_invalid_q2_code_cannot_expand_examples_to_all_intentions(self):
        with (
            patch.object(haystack_rag, "_get_intention_label_from_code", return_value=None),
            patch.object(haystack_rag, "get_q3_triggers") as triggers,
        ):
            self.assertEqual(haystack_rag._get_q3_triggers_affichage(
                [], "relation_client", "99", "Cabinet & conseil",
            ), "")
            triggers.assert_not_called()

    def test_q3_prefers_contextual_examples_from_distinct_cases(self):
        docs = [
            SimpleNamespace(meta={
                "case_id": f"UC-{i:04d}", "intention": "Objectif", "secteur": "Multi-sectoriel",
                "cas_utilisation": title, "declencheurs_typiques": triggers,
            })
            for i, (title, triggers) in enumerate((
                ("Centraliser les commandes", "analyse abstraite | commandes dispersées | commandes en doublon"),
                ("Comparer les contrats", "amélioration souhaitée | contrats introuvables"),
                ("Préparer les factures", "adhésion limitée | factures incomplètes"),
                ("Organiser les livraisons", "analyse tardive | livraisons décalées"),
            ), start=1)
        ]
        with patch.object(haystack_rag, "_fetch_documents_for_domaine", return_value=docs):
            pool = haystack_rag.build_pool("achats_fournisseurs", "Objectif", "Autre / Non spécifique")
            examples = haystack_rag.get_q3_triggers("achats_fournisseurs", "Objectif", "Autre / Non spécifique")
        self.assertEqual(examples, [
            "commandes dispersées", "contrats introuvables", "factures incomplètes", "livraisons décalées",
        ])
        self.assertEqual(examples, pool[:4])
        self.assertEqual(len(pool), 9)

    def test_q3_chunk_repetition_and_input_order_do_not_change_selection(self):
        docs = [
            SimpleNamespace(id=f"chunk-{i}", meta={
                "case_id": f"UC-{i:04d}", "intention": "Objectif",
                "cas_utilisation": title, "declencheurs_typiques": triggers,
            })
            for i, (title, triggers) in enumerate((
                ("Classer les dossiers", "dossiers dispersés | dossiers incomplets"),
                ("Suivre les demandes", "demandes perdues | demandes répétées"),
                ("Organiser les réunions", "réunions sans suivi"),
                ("Préparer les rapports", "rapports en retard"),
            ), start=1)
        ]
        with patch.object(haystack_rag, "_fetch_documents_for_domaine", return_value=docs):
            expected = haystack_rag.get_q3_triggers("relation_client", "Objectif")
        duplicates = [SimpleNamespace(id=f"duplicate-{i}", meta=dict(docs[0].meta)) for i in range(40)]
        for ordering in (docs + duplicates, list(reversed(docs + duplicates))):
            with patch.object(haystack_rag, "_fetch_documents_for_domaine", return_value=ordering):
                self.assertEqual(haystack_rag.get_q3_triggers("relation_client", "Objectif"), expected)
        self.assertEqual(len(expected), 4)
        self.assertEqual(sum(t.startswith("dossiers") for t in expected), 1)

    def test_q3_diversifies_context_terms_before_repeating_a_topic(self):
        docs = [
            SimpleNamespace(meta={
                "case_id": f"UC-{i:04d}", "intention": "Objectif",
                "cas_utilisation": title, "declencheurs_typiques": trigger,
            })
            for i, (title, trigger) in enumerate((
                ("Classer les dossiers", "dossiers absents"),
                ("Classer les dossiers", "dossiers incomplets"),
                ("Classer les dossiers", "dossiers perdus"),
                ("Suivre les tickets", "tickets oubliés"),
                ("Préparer les rapports", "rapports en retard"),
            ), start=1)
        ]
        with patch.object(haystack_rag, "_fetch_documents_for_domaine", return_value=docs):
            examples = haystack_rag.get_q3_triggers("relation_client", "Objectif", top_k=3)
        self.assertEqual(examples, ["dossiers absents", "rapports en retard", "tickets oubliés"])

    def test_q3_defers_near_duplicate_wordings_from_different_cases(self):
        docs = [
            SimpleNamespace(meta={
                "case_id": f"UC-{i:04d}", "intention": "Objectif",
                "cas_utilisation": title, "declencheurs_typiques": trigger,
            })
            for i, (title, trigger) in enumerate((
                ("Consolider les tickets clients", "tickets clients non classés globalement"),
                ("Consolider les tickets internes", "tickets internes non classés globalement"),
                ("Classer les dossiers", "dossiers incomplets"),
                ("Préparer les rapports", "rapports en retard"),
                ("Suivre les devis", "devis sans réponse"),
            ), start=1)
        ]
        with patch.object(haystack_rag, "_fetch_documents_for_domaine", return_value=docs):
            pool = haystack_rag.build_pool("relation_client", "Objectif")
            shown = haystack_rag.get_q3_triggers("relation_client", "Objectif")
        self.assertEqual(len(pool), 5)
        self.assertEqual(shown, pool[:4])
        self.assertEqual(sum(text.startswith("tickets") for text in shown), 1)
        self.assertEqual(pool[-1], "tickets internes non classés globalement")

    def test_q3_redundancy_is_conservative_and_never_drops_source_examples(self):
        words = haystack_rag._query_keywords
        self.assertFalse(haystack_rag._q3_examples_overlap(set(), set()))
        self.assertFalse(haystack_rag._q3_examples_overlap(
            set(words("factures en retard")), set(words("factures incomplètes"))))
        self.assertTrue(haystack_rag._q3_examples_overlap(
            set(words("coûts de traitement élevés")), set(words("coûts traitement élevés"))))
        docs = [SimpleNamespace(meta={
            "case_id": "UC-0001", "intention": "Objectif",
            "declencheurs_typiques": "coûts de traitement élevés | coûts traitement élevés",
        })]
        with patch.object(haystack_rag, "_fetch_documents_for_domaine", return_value=docs):
            self.assertEqual(haystack_rag.get_q3_triggers("relation_client", "Objectif"),
                             ["coûts de traitement élevés", "coûts traitement élevés"])

    def test_q3_keeps_exact_sector_priority_and_source_order_without_lexical_match(self):
        docs = [
            SimpleNamespace(meta={
                "case_id": "UC-0001", "intention": "Objectif", "secteur": "Industrie",
                "declencheurs_typiques": "Zéro suivi | Analyse tardive",
            }),
            SimpleNamespace(meta={
                "case_id": "UC-0002", "intention": "Objectif", "secteur": "Multi-sectoriel",
                "cas_utilisation": "Suivre les commandes", "declencheurs_typiques": "commandes dispersées",
            }),
        ]
        with patch.object(haystack_rag, "_fetch_documents_for_domaine", return_value=docs):
            self.assertEqual(haystack_rag.get_q3_triggers("achats_fournisseurs", "Objectif", "Industrie"),
                             ["Zéro suivi", "Analyse tardive", "commandes dispersées"])
            self.assertEqual(haystack_rag.get_q3_triggers("achats_fournisseurs", "Objectif", "Autre"),
                             ["commandes dispersées"])

    def test_q3_missing_ids_and_normalized_duplicates_keep_source_text(self):
        docs = [
            SimpleNamespace(meta={"intention": "Objectif", "cas_utilisation": "Suivre les échanges",
                                  "declencheurs_typiques": " | Échanges   dispersés | échanges disperses | suivi absent"}),
            SimpleNamespace(meta={"intention": "Objectif", "cas_utilisation": "Préparer les devis",
                                  "declencheurs_typiques": "devis en retard"}),
        ]
        with patch.object(haystack_rag, "_fetch_documents_for_domaine", return_value=docs * 10):
            pool = haystack_rag.build_pool("relation_client", "Objectif")
        self.assertEqual(pool, ["devis en retard", "Échanges   dispersés", "suivi absent"])

    def test_q3_source_variants_and_shared_examples_keep_sector_provenance(self):
        docs = [
            SimpleNamespace(meta={
                "Code du cas": "UC-0001", "intention": "Objectif", "secteur": "Industrie",
                "cas_utilisation": "Suivre les échanges", "Trigger": "Échanges   dispersés | suivi absent",
            }),
            SimpleNamespace(meta={
                "Code du cas": "UC-0002", "intention": "Objectif", "secteur": "Multi-sectoriel",
                "cas_utilisation": "Suivre les échanges", "Trigger": "echanges disperses",
            }),
        ]
        for ordering in (docs, list(reversed(docs)), docs * 5):
            with patch.object(haystack_rag, "_fetch_documents_for_domaine", return_value=ordering):
                self.assertEqual(haystack_rag.get_q3_triggers("relation_client", "Objectif", "Industrie"),
                                 ["Échanges   dispersés", "suivi absent"])
                self.assertEqual(haystack_rag.get_q3_triggers("relation_client", "Objectif", "Autre"),
                                 ["echanges disperses"])

    def test_q3_contextual_ranking_is_not_specific_to_purchasing(self):
        for domain, intention, title, source in (
            ("ressources_humaines", "Recruter", "Comparer les candidatures",
             "analyse insuffisante | candidatures dispersées"),
            ("stocks_logistique", "Organiser les stocks", "Suivre les inventaires",
             "amélioration souhaitée | inventaires incohérents"),
            ("marketing_visibilite", "Créer des contenus", "Préparer les brochures",
             "adhésion limitée | brochures obsolètes"),
        ):
            with self.subTest(domain=domain):
                doc = SimpleNamespace(meta={
                    "case_id": "UC-0001", "intention": intention, "secteur": "Multi-sectoriel",
                    "cas_utilisation": title, "declencheurs_typiques": source,
                })
                with patch.object(haystack_rag, "_fetch_documents_for_domaine", return_value=[doc]):
                    self.assertEqual(haystack_rag.get_q3_triggers(domain, intention, "Autre", top_k=1),
                                     [source.split("|")[1].strip()])

    def test_q3_introduction_does_not_claim_frequency_or_change_examples(self):
        with patch.object(haystack_rag, "get_q15_choices", return_value=[]):
            response = haystack_rag._qualification_response(
                "relation_client", None, "1", "", "", "- Échanges   dispersés", None,
            )
        self.assertIn("exemples de problèmes liés à cet objectif", response)
        self.assertNotIn("fréquentes", response)
        self.assertIn("- Échanges   dispersés\n", response)
        self.assertTrue(response.endswith("Décrivez votre situation en une ou deux phrases."))

    def test_q3_generalizes_to_all_domains_without_changing_eligible_pool(self):
        for domain in haystack_rag.CHOIX_Q1_TO_DOMAINE_CODE.values():
            sectors = haystack_rag.SECTEURS_PAR_DOMAINE.get(domain, [])
            selections = (None, "Autre / Non spécifique", *sectors)
            docs = [
                SimpleNamespace(meta={
                    "case_id": f"UC-{i:04d}", "domaine": domain, "intention": objective,
                    "secteur": sector, "cas_utilisation": title, "declencheurs_typiques": triggers,
                })
                for i, (objective, sector, title, triggers) in enumerate((
                    ("Objectif A", "Multi-sectoriel", "Suivre les commandes",
                     "analyse tardive | commandes dispersées | commandes incomplètes"),
                    ("Objectif A", "Multi-sectoriel", "Suivre les factures",
                     "amélioration souhaitée | factures perdues"),
                    ("Objectif A", sectors[0] if sectors else "Industrie", "Suivre les dossiers",
                     "adhésion limitée | dossiers incomplets"),
                    ("Objectif B", "Multi-sectoriel", "Comparer les contrats", "contrats introuvables"),
                ), start=1)
            ]
            for sector in selections:
                for objective in ("Objectif A", "Objectif B", "Objectif absent"):
                    with self.subTest(domain=domain, sector=sector, objective=objective):
                        eligible = [
                            doc for doc in docs if doc.meta["intention"] == objective
                            and (not sector or haystack_rag._doc_is_applicable_to_sector(doc, sector))
                        ]
                        expected = {t.strip() for doc in eligible
                                    for t in doc.meta["declencheurs_typiques"].split("|")}
                        with patch.object(haystack_rag, "_fetch_documents_for_domaine", return_value=docs):
                            pool = haystack_rag.build_pool(domain, objective, sector)
                            shown = haystack_rag.get_q3_triggers(domain, objective, sector)
                        self.assertEqual(set(pool), expected)
                        self.assertEqual(shown, pool[:4])
                        with patch.object(haystack_rag, "_fetch_documents_for_domaine",
                                          return_value=list(reversed(docs)) * 3):
                            self.assertEqual(haystack_rag.get_q3_triggers(domain, objective, sector), shown)

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


class HaystackRagReplyExtractionTests(unittest.TestCase):
    def test_reply_to_text_handles_chatmessage_str_and_none(self):
        from haystack.dataclasses import ChatMessage

        self.assertEqual(haystack_rag._reply_to_text(ChatMessage.from_assistant("hi")), "hi")
        self.assertEqual(haystack_rag._reply_to_text("plain"), "plain")
        self.assertEqual(haystack_rag._reply_to_text(None), "")


class HaystackRagAuthoritativeParcoursTests(unittest.TestCase):
    def test_selection_returns_authoritative_parcours_url_and_label(self):
        """
        Régression bouton parcours : quand l'utilisateur sélectionne un cas (chiffre seul),
        get_rag_prompt_and_sources doit renvoyer l'URL et le libellé du parcours du cas
        RÉELLEMENT choisi (positions 9 et 10 du tuple), pour un bouton fiable côté frontend.
        """
        cases = [
            {"id": "UC-0001", "content": "c1"},
            {"id": "UC-0002", "content": "c2"},
            {"id": "UC-0003", "content": "c3"},
        ]
        niveau2_payload = ("Réponse détail cas 3", ["src"], ["UC-0001", "UC-0002", "UC-0003"], ["c1", "c2", "c3"], [{}, {}, {}])

        with (
            patch.object(haystack_rag, "_build_niveau2_detail_payload", return_value=niveau2_payload),
            patch.object(
                haystack_rag,
                "build_parcours_info",
                return_value={"parcours_url": "https://host/action-abc.html", "cta_label": "🚀 Démarrer (UC-0003)"},
            ) as mock_info,
        ):
            result = haystack_rag.get_rag_prompt_and_sources(
                "3",
                history=[{"role": "user", "content": "3"}],
                last_suggested_cases=cases,
            )

        niveau2_answer = result[8]
        selected_url = result[9]
        selected_label = result[10]
        self.assertEqual(niveau2_answer, "Réponse détail cas 3")
        self.assertEqual(selected_url, "https://host/action-abc.html")
        self.assertEqual(selected_label, "🚀 Démarrer (UC-0003)")
        # L'URL est bien calculée pour le cas sélectionné (UC-0003), pas un autre.
        mock_info.assert_called_once_with("UC-0003")


class HaystackRagParcoursPitchDedupTests(unittest.TestCase):
    def test_niveau2_detail_does_not_duplicate_parcours_pitch(self):
        """
        Régression bloc "Passez à l'action" dupliqué : si le bloc niveau 2 contient déjà
        le pitch parcours, _build_niveau2_detail_payload ne doit pas en rajouter un second.
        """
        from app.parcours_util import PARCOURS_PITCH_SENTINEL, get_parcours_pitch

        cases = [{"id": "UC-0152", "content": "Optimiser vos pages web pour convertir"}]
        # Le bloc niveau 2 construit contient DÉJÀ le pitch (sentinelle présente).
        block_with_pitch = "Détail du cas.\n\n" + get_parcours_pitch()["message_suffix"]

        with (
            patch.object(
                haystack_rag,
                "_enrich_case_from_document_store",
                return_value={
                    "id": "UC-0152",
                    "content": "Optimiser vos pages web pour convertir plus de visiteurs (contenu long).",
                    "description_cas_utilisation": "desc",
                    "secteur": "Commerce & retail",
                    "declencheurs_typiques": "pages peu performantes",
                },
            ),
            patch.object(haystack_rag, "_run_pertinence_llm", return_value="Votre situation..."),
            patch.object(haystack_rag, "build_niveau2_block", return_value=block_with_pitch),
            patch.object(
                haystack_rag,
                "build_parcours_info",
                return_value={"parcours_url": "https://h/action-x.html", "cta_label": "🚀 Démarrer"},
            ),
        ):
            result = haystack_rag._build_niveau2_detail_payload(0, cases, [], "1")

        self.assertIsNotNone(result)
        answer = result[0]
        self.assertEqual(
            answer.count(PARCOURS_PITCH_SENTINEL),
            1,
            f"Le pitch parcours ne doit apparaître qu'une fois, trouvé {answer.count(PARCOURS_PITCH_SENTINEL)}x.",
        )


class HaystackRagNiveau2VerbatimCardTests(unittest.TestCase):
    def test_build_niveau2_block_is_verbatim_and_lean(self):
        """
        La carte niveau 2 doit être 100% verbatim (règle D1) : titre + badges + description +
        déclencheurs, SANS le détail opérationnel (prérequis/première action/guardrails/auto-diagnostic)
        qui vit désormais dans le parcours, et SANS phrase de pertinence générée par l'IA.
        """
        case = {
            "cas_utilisation": "Créer des infographies et affiches commerciales percutantes",
            "description_cas_utilisation": "L'IA conçoit le contenu de vos infographies. Vos supports deviennent plus percutants.",
            "effort": "Faible",
            "mode_execution": "no_code",
            "sensibilite_donnees": "Données publiques",
            "declencheurs_typiques": "arguments difficiles à visualiser|supports peu attractifs",
            # Champs qui NE doivent PAS apparaître (ils sont dans le parcours) :
            "prerequis_donnees": "Données chiffrées à mettre en valeur",
            "premiere_action_48h": "Rassembler les 3 à 5 données chiffrées",
            "guardrails": "Anonymiser toutes les données personnelles",
            "questions_qualification": "Les visuels sont-ils standardisés ?",
        }
        out = haystack_rag.build_niveau2_block(case)

        # Présents (verbatim)
        self.assertIn("Créer des infographies et affiches commerciales percutantes", out)
        self.assertIn("Sans code", out)  # mapping mode_execution
        self.assertIn("Effort faible", out)
        self.assertIn("Données publiques", out)
        self.assertIn("Vos supports deviennent plus percutants.", out)  # description verbatim
        self.assertIn("supports peu attractifs", out)  # déclencheur verbatim

        # Absents (déplacés vers le parcours) + aucune phrase de pertinence IA
        for forbidden in (
            "Ce qu'il vous faut",
            "Première étape",
            "Point de vigilance",
            "Auto-diagnostic",
            "Pourquoi c'est pertinent",
            "Données chiffrées à mettre en valeur",
            "Anonymiser toutes les données personnelles",
        ):
            self.assertNotIn(forbidden, out)

    def test_mode_execution_label_maps_known_values(self):
        self.assertEqual(haystack_rag._mode_execution_label("no_code"), "Sans code")
        self.assertEqual(haystack_rag._mode_execution_label("outil"), "Avec un outil")
        # Valeur inconnue : renvoyée telle quelle (pas de génération)
        self.assertEqual(haystack_rag._mode_execution_label("Autre mode"), "Autre mode")


if __name__ == "__main__":
    unittest.main()
