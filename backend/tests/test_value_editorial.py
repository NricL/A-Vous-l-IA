import copy
import html
import os
from pathlib import Path
import unittest

from app import value_editorial as editorial_module
from app.value_editorial import editorial_for, load_editorial, source_fields, source_fingerprint, SOURCE_FIELDS
from app.value_contract import value_presentation
from scripts.editorial_sources import extract
from scripts.validate_value_editorial import validate_rows

APP_ROOT = Path(editorial_module.__file__).resolve().parent

class EditorialContractTests(unittest.TestCase):
    def setUp(self):
        self.source = {
            "cas_utilisation": "Comparer les devis",
            "description_cas_utilisation": "Aligner les postes comparables pour examiner les écarts.",
            "premiere_action_48h": "Produire une grille de comparaison avec les écarts en %. Vérifier les unités.",
            "guardrails": "Le responsable achats valide la comparaison avant engagement.",
        }
        self.fields = source_fields(self.source)
        self.snapshot = {"case_id": "UC-1003", "fields": self.fields,
                         "source_fingerprint": source_fingerprint(self.fields)}
        definitions = {
            "gain": ("Mieux repérer les différences entre postes réellement comparables.", "description", "postes comparables"),
            "deliverable": ("Une grille de comparaison à examiner.", "first_action", "grille de comparaison"),
            "horizon": ("Après vérification des unités et validation de la comparaison.", "guardrails", "valide la comparaison"),
            "useful_when": ("Si vous devez examiner des devis portant sur des postes comparables.", "description", "postes comparables"),
            "tradeoff": ("Vérifier les unités et faire valider la comparaison avant engagement.", "guardrails", "avant engagement"),
        }
        self.row = {"case_id": "UC-1003", "source_fingerprint": self.snapshot["source_fingerprint"],
                    "review_status": "authored_source_reviewed", "horizon_kind": "first_reviewed_output",
                    "claims": {name: {"text": text, "evidence": [{"field": field, "quote": quote}],
                                      "unknown_reason": None} for name, (text, field, quote) in definitions.items()},
                    "review_note": "Les écarts de devis ne sont pas une économie réalisée ; engagement soumis à validation achats."}

    def check_row(self, row):
        return validate_rows([row], [self.snapshot])

    def test_grounded_comparison_does_not_turn_quote_percentages_into_roi(self):
        self.assertEqual(len(self.check_row(self.row)), 1)
        changed = copy.deepcopy(self.row)
        changed["claims"]["gain"]["text"] = "Économiser 20 % sur les achats."
        changed["claims"]["gain"]["evidence"] = [{"field": "first_action", "quote": "écarts en %"}]
        with self.assertRaises(ValueError):
            self.check_row(changed)

    def test_exact_anchor_does_not_authorize_autonomous_or_deployed_scope(self):
        for text in ("Une décision automatique sur le fournisseur.", "Un comparateur déployé en production."):
            with self.subTest(text=text):
                changed = copy.deepcopy(self.row)
                changed["claims"]["deliverable"]["text"] = text
                with self.assertRaises(ValueError):
                    self.check_row(changed)

    def test_first_review_condition_is_not_a_guarantee_or_certification(self):
        for text in ("Une comparaison garantie sans erreur.", "Une conformité acquise.", "Un fournisseur certifié."):
            with self.subTest(text=text):
                changed = copy.deepcopy(self.row)
                changed["claims"]["gain"]["text"] = text
                with self.assertRaises(ValueError):
                    self.check_row(changed)

    def test_unknown_is_explicit_not_counted_as_authored(self):
        changed = copy.deepcopy(self.row)
        changed["claims"]["horizon"] = {"text": None, "evidence": [],
                                        "unknown_reason": "Aucune condition d'observation décrite."}
        changed["horizon_kind"] = "unknown"
        checked = self.check_row(changed)[0]
        self.assertIsNone(checked["claims"]["horizon"]["text"])
        changed["claims"]["horizon"]["unknown_reason"] = None
        with self.assertRaises(ValueError):
            self.check_row(changed)

    def test_wrong_field_or_invented_quote_rejected(self):
        changed = copy.deepcopy(self.row)
        changed["claims"]["gain"]["evidence"][0]["field"] = "title"
        with self.assertRaises(ValueError):
            self.check_row(changed)

    def test_identity_and_every_source_field_bind_the_editorial_layer(self):
        registry = {"UC-1003": self.row}
        self.assertIsNotNone(editorial_for("UC-1003", self.source, registry))
        self.assertIsNone(editorial_for("UC-0001", self.source, registry))
        for key in self.source:
            changed = {**self.source, key: self.source[key] + " changed"}
            self.assertIsNone(editorial_for("UC-1003", changed, registry))

    def test_newline_normalization_does_not_rewrite_source(self):
        fields = {**self.fields, "description": "Une ligne.\r\nUne autre."}
        unix = {**fields, "description": fields["description"].replace("\r\n", "\n")}
        self.assertEqual(source_fingerprint(fields), source_fingerprint(unix))
        self.assertIn("\r\n", fields["description"])

    def test_html_decoded_once_and_unrelated_presentation_not_fingerprinted(self):
        page = ('<h1>Devis</h1><p class="resume source">A &amp;amp; B</p>'
                '<section data-etape="3"><p class="source">Relire &amp;amp; valider.</p></section>'
                '<section data-etape="4"><p class="source">Faire une grille.\n\nPuis vérifier.</p></section>'
                '<p>base Avoulia v4.6.3 — cas UC-1003.</p>')
        first = extract(page, "action-test.html")
        second = extract(page + '<footer>Un nouvel affichage.</footer>', "action-test.html")
        self.assertEqual(first["fields"]["description"], "A &amp; B")
        self.assertEqual(first["fields"]["guardrails"], "Relire &amp; valider.")
        self.assertEqual(first["fields"]["first_action"], "Faire une grille.\n\nPuis vérifier.")
        self.assertEqual(first["source_fingerprint"], second["source_fingerprint"])

    def test_complete_authored_universe_does_not_claim_measured_value(self):
        registry = load_editorial()
        self.assertEqual(len(registry), 1021)
        self.assertEqual(sum(len(r["claims"]) for r in registry.values()), 5105)
        for row in registry.values():
            self.assertEqual(set(row["claims"]), {"gain", "deliverable", "horizon", "useful_when", "tradeoff"})
            self.assertNotIn("review_note", row)

    def test_four_reviewed_samples_preserve_sources_and_conditional_value(self):
        pages = APP_ROOT / "static" / "parcours"
        samples = {"UC-0706": "action-qjpbbj2u6e.html", "UC-0725": "action-8kn25a5yeq.html",
                   "UC-0734": "action-224f2erma7.html", "UC-1003": "action-cww76mv3h8.html"}
        for identity, page in samples.items():
            with self.subTest(identity=identity):
                record = extract((pages / page).read_text(encoding="utf-8"), page)
                source = {SOURCE_FIELDS[k]: v for k, v in record["fields"].items()}
                before = copy.deepcopy(source)
                value = value_presentation(source, identity)
                self.assertEqual(value["status"], "editorial_hypothesis")
                self.assertEqual(value["description"], source["description_cas_utilisation"])
                self.assertEqual(value["first_action"], source["premiere_action_48h"])
                self.assertIsNone(value["measured_gain"])
                self.assertIsNone(value["elapsed_horizon"])
                self.assertEqual(source, before)
                self.assertNotIn("fait gagner", value["editorial"]["claims"]["gain"]["text"])
                self.assertIn("non établis", value["limit"])

    def test_editorial_upgrade_changes_only_owned_entry_and_matches_api(self):
        root = os.environ.get("PARCOURS_SOURCE_ROOT")
        if not root:
            self.skipTest("PARCOURS_SOURCE_ROOT required")
        from jinja2 import Environment, FileSystemLoader, select_autoescape
        from scripts.publish_editorial_pages import transform
        template = Environment(loader=FileSystemLoader(Path(root) / "templates"),
                               autoescape=select_autoescape(("html", "html.j2"))).get_template("value-entry.html.j2")
        page = "action-cww76mv3h8.html"
        original = (APP_ROOT / "static/parcours" / page).read_text(encoding="utf-8")
        rendered, record = transform(original, page, template)
        value = editorial_for(record["case_id"], {SOURCE_FIELDS[k]: v for k, v in record["fields"].items()})
        for claim in value["claims"].values():
            self.assertIn(claim["text"], html.unescape(rendered))
        self.assertIn("editorial-value-2", rendered)
        self.assertNotIn("source-value-1", rendered.split("<!-- /value-entry -->")[0])
        self.assertEqual((Path(root) / "pipeline/value_editorial.py").read_bytes(),
                         (APP_ROOT / "value_editorial.py").read_bytes())
        self.assertEqual((Path(root) / "pipeline/content/value_editorial.json").read_bytes(),
                         (APP_ROOT / "content/value_editorial.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
