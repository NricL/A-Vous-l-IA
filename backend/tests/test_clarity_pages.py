"""Public HTML and synthetic prompts only; no catalogue/workbook loading."""
import copy
import html
import importlib.util
import os
from pathlib import Path
import re
import unittest
from unittest.mock import patch

from scripts.publish_clarity_pages import check_prompts, load_rendering, public_case, section, transform

ROOT = Path(__file__).resolve().parents[1]


class ClarityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get("PARCOURS_SOURCE_ROOT")
        if not source:
            raise unittest.SkipTest("PARCOURS_SOURCE_ROOT required")
        cls.source = Path(source)
        cls.rendering = load_rendering(cls.source)
        cls.prompts = cls.rendering[0]
        cls.page = "action-cww76mv3h8.html"
        cls.original = (ROOT / "app/static/parcours" / cls.page).read_text(encoding="utf-8")
        cls.case = public_case(cls.original, cls.page)[0]

    def test_public_reconstruction_and_private_generator_match_exactly(self):
        spec = importlib.util.spec_from_file_location("clarity_generator", self.source / "pipeline/genere.py")
        generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generator)
        updated, _, case = transform(self.original, self.page, self.rendering)
        with patch.object(generator, "charge_base", side_effect=AssertionError("No workbook access")), \
                patch.object(generator, "load_workbook", side_effect=AssertionError("No workbook access")), \
                patch.object(generator.pd, "read_excel", side_effect=AssertionError("No workbook access")):
            direct = generator.render_page(case, self.page[7:-5], "v4.6.3", generator.load_template(),
                                           self.rendering[2], app_url=public_case(self.original, self.page)[1])
        self.assertEqual(updated, direct)

    def test_standalone_role_input_output_and_exact_source_for_every_prompt_type(self):
        before = copy.deepcopy(self.case)
        prompts = [self.prompts.prompt_preparation(self.case, p) for p in self.case["prereqs"]]
        prompts += [self.prompts.prompt_principal(self.case), self.prompts.prompt_reutilisation(self.case)]
        for prompt in prompts:
            for value in (self.case["cas_utilisation"], self.case["premiere_action_48h"], self.case["guardrails"]):
                self.assertIn(value, prompt)
            self.assertTrue(prompt.startswith("Tu m'aides"))
            self.assertIn("[", prompt)
            self.assertNotRegex(prompt, r"(?i)étape\s*[1-6]|ci-dessus|déjà fournis plus haut")
            self.assertIn("crochets non complétés ne sont pas des données", prompt)
            self.assertIn("trois questions", prompt)
        self.assertEqual(before, self.case)

    def test_preparation_distinguishes_real_document_draft_profile_access_and_rule(self):
        inputs = ["Historique de ventes", "Contrat signé", "Profil client",
                  "Brouillon à créer", "Accès à un outil", "Validation par le responsable"]
        for element in inputs:
            prompt = self.prompts.prompt_preparation(self.case, element)
            self.assertIn("Élément source à préparer : " + element, prompt)
            self.assertIn("UNE entrée", prompt)
            self.assertIn("UN SEUL format", prompt)
            self.assertIn("Ne réalise pas encore le livrable final", prompt)
            self.assertIn("original de tes annotations", prompt)
            self.assertIn("ne déduis pas de caractéristiques", prompt)
            self.assertIn("ni mot de passe, ni clé", prompt)
            self.assertIn("si cet élément désigne lui-même".casefold(), prompt.casefold())

    def test_production_consumes_actual_content_not_a_reference_to_absent_documents(self):
        prompt = self.prompts.prompt_principal(self.case)
        self.assertIn("ne donne pas accès à leur contenu", prompt)
        self.assertIn("Ne recommence ni le questionnaire", prompt)
        self.assertIn("ne les refais pas", prompt)
        self.assertIn("pas une nouvelle liste de prérequis", prompt)
        self.assertIn("Ne réalise pas le test terrain", prompt)
        self.assertIn("sans vérification récente".casefold(), prompt.casefold())

    def test_reuse_outputs_instructions_not_the_task_or_an_agent_install(self):
        prompt = self.prompts.prompt_reutilisation(self.case)
        for fragment in ("pas à exécuter la tâche", "UNE consigne courte", "champs variables",
                         "Ma méthode testée", "À compléter et tester", "sans exiger un abonnement",
                         "Ne conserve pas les données du précédent essai", "règles source exactes"):
            self.assertIn(fragment, prompt)
        updated, _, _ = transform(self.original, self.page, self.rendering)
        self.assertIn("Sinon, copiez-la dans une nouvelle conversation", section(updated, 6))
        self.assertIn("n'automatise pas l'exécution", section(updated, 6))

    def test_production_and_reuse_are_inline_in_their_steps_not_a_bottom_detour(self):
        updated, _, c = transform(self.original, self.page, self.rendering)
        self.assertIn('id="prompt-demarrage"', section(updated, 4))
        self.assertIn('id="prompt-reutilisation"', section(updated, 6))
        self.assertNotIn("<pre>", section(updated, 5))
        self.assertNotIn("quickwin-accordion", updated)
        self.assertNotIn("lien-retour", updated)
        self.assertNotIn("Revenir volontairement", updated)
        self.assertNotIn("Gardez le lien", updated)
        check_prompts(updated, c, self.prompts)

    def test_displayed_prompt_mutation_fails_closed_and_source_references_remain_exact(self):
        updated, _, c = transform(self.original, self.page, self.rendering)
        with self.assertRaisesRegex(ValueError, "prompt contract"):
            check_prompts(updated.replace("Tu m&#39;aides", "Reprends l&#39;étape 2", 1), c, self.prompts)
        special = {**c, "guardrails": "Règle source : étape 2 du protocole <A & B>."}
        prompt = self.prompts.prompt_principal(special)
        self.assertIn(special["guardrails"], prompt)

    def test_editorial_provenance_not_deleted_and_all_claims_remain_visible_in_context(self):
        from app.value_editorial import editorial_for
        updated, _, _ = transform(self.original, self.page, self.rendering)
        value = editorial_for(self.case["use_case_id"], self.case)
        for claim in value["claims"].values():
            self.assertTrue(claim["evidence"])
            self.assertIn(claim["text"], html.unescape(updated))
        entry = re.search(r"<!-- value-entry:.*?<!-- /value-entry -->", updated, re.S)[0]
        self.assertNotIn("<details>", entry)
        self.assertNotIn("Passages source", entry)
        self.assertIn("Le bénéfice dépend de votre situation", entry)


if __name__ == "__main__":
    unittest.main()
