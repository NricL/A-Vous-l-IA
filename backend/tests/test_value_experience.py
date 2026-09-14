import copy
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.value_contract import HORIZON, LIMIT, TRADEOFF, USEFUL_WHEN, value_presentation
from scripts.publish_value_pages import transform


class ValueContractTests(unittest.TestCase):
    def test_verbatim_source_and_no_inferred_gain(self):
        source = {"description_cas_utilisation": "  Exemple <source> & détail\n",
                  "premiere_action_48h": "Action exacte.", "effort": "Faible"}
        before = copy.deepcopy(source)
        value = value_presentation(source)
        self.assertEqual(value["description"], source["description_cas_utilisation"])
        self.assertEqual(value["first_action"], source["premiere_action_48h"])
        self.assertEqual(value["status"], "source_only")
        self.assertEqual(value["horizon"], HORIZON)
        self.assertNotIn("gain", value)
        self.assertEqual(source, before)

    def test_missing_values_remain_unknown(self):
        for source in ({}, {"effort": " ", "premiere_action_48h": 48}):
            value = value_presentation(source)
            self.assertIsNone(value["description"])
            self.assertIsNone(value["first_action"])
            self.assertIsNone(value["effort"])

    def test_request_value_cannot_enter_business_fields(self):
        from app.models import SuggestedCase
        value = SuggestedCase(id="UC-0001", content="Source", value_presentation={"gain": "untrusted"})
        self.assertEqual(value.content, "Source")
        self.assertIsNone(value.description_cas_utilisation)

    def test_routes_attach_value_and_ignore_client_presentation(self):
        from test_chat_relevance import routes
        from app.models import ChatRequest
        from app.rag_constants import Q1_DOMAINS_LIST, WELCOME_MESSAGE
        welcome = routes.chat_welcome()
        self.assertEqual(welcome["message"], WELCOME_MESSAGE)
        self.assertEqual(welcome["initial_question"].splitlines()[2:],
                         [f"{i}. {label}" for i, label in enumerate(Q1_DOMAINS_LIST, 1)])
        source = {"description_cas_utilisation": "Exact.", "premiere_action_48h": "Faire."}
        with patch.object(routes, "build_parcours_info", return_value={}):
            cases = routes._build_suggested_cases(["UC-0001"], ["Source"], [source])
        self.assertEqual(cases[0].value_presentation, value_presentation(source))
        request = ChatRequest(message="1", last_suggested_cases=cases)
        self.assertNotIn("value_presentation", routes._last_suggested_cases_to_dicts(request)[0])

    def test_parcours_contract_and_escape(self):
        root = os.environ.get("PARCOURS_SOURCE_ROOT")
        if not root:
            self.skipTest("PARCOURS_SOURCE_ROOT required")
        env = Environment(loader=FileSystemLoader(Path(root) / "templates"),
                          autoescape=select_autoescape(("html", "html.j2")))
        text = """<header><h1>Source</h1></header>
<h2>Commencez par un petit essai</h2>
<pre>Première action source : Faire &lt;script&gt; &amp; vérifier.

Fin du prompt</pre>
<section data-etape="1"></section><section data-etape="2"></section>
<section data-etape="3"></section><section data-etape="4"><p class="source">Faire &lt;script&gt; &amp; vérifier.

Conserver aussi ce second paragraphe.</p></section>
<section data-etape="5"><div class="valider"><input type="checkbox" id="fin-5"></div></section>
<section data-etape="6"><div class="valider"><input type="checkbox" id="fin-6"></div></section>
<footer>base Avoulia v4.6.3 — cas UC-0001.</footer></body>"""
        result, evidence = transform(text, env)
        for constant in (HORIZON, LIMIT, USEFUL_WHEN, TRADEOFF):
            self.assertIn(constant, result)
        self.assertIn("Faire &lt;script&gt; &amp; vérifier.", result)
        self.assertNotIn("Faire <script>", result)
        self.assertEqual(result.count("Conserver aussi ce second paragraphe."), 2)
        self.assertEqual(evidence["case_id"], "UC-0001")
        self.assertEqual(result.count('id="bilan-temps"'), 1)
        self.assertIn("location.origin+location.pathname", result)
        self.assertNotIn("fetch(", result)
        with self.assertRaises(ValueError):
            transform(result, env)


if __name__ == "__main__":
    unittest.main()
