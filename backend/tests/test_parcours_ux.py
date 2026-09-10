import copy
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import unittest
from html.parser import HTMLParser
from unittest.mock import patch

from app import parcours_util


PARCOURS_ROOT = Path(os.environ.get(
    "PARCOURS_SOURCE_ROOT",
    Path(__file__).resolve().parents[3] / "parcours-src" / "avoulia-parcours",
))


def synthetic_case(mode="outil"):
    return {
        "use_case_id": "SYNTHETIC-UX",
        "cas_utilisation": 'Cas fictif « équipe & qualité » <à conserver>',
        "description_cas_utilisation": "Texte source : Je suis dirigeant.\nLigne intacte.",
        "domaine_label": "Domaine fictif",
        "intention": "Intention fictive",
        "effort": "Effort source inchangé",
        "sensibilite_donnees": "Sensibilité fictive",
        "mode_execution": mode,
        "questions": ["Question fictive une ?", "Question fictive deux ?", "Question fictive trois ?"],
        "prereqs": ['Document fictif "A & B" <interne>', "Élément fictif deux"],
        "guardrails": "Règle fictive <sans données réelles>.\nValidation fictive.",
        "guardrails_liste": ["Règle fictive <sans données réelles>.", "Validation fictive."],
        "premiere_action_48h": "Action source : conserver chaque mot, espace & signe <ici>.",
    }


class PageParser(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.text = []
        self.pre = []
        self.in_pre = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))
        if tag == "pre":
            self.in_pre = True
            self.pre.append("")

    def handle_endtag(self, tag):
        if tag == "pre":
            self.in_pre = False

    def handle_data(self, data):
        self.text.append(data)
        if self.in_pre:
            self.pre[-1] += data


class ParcoursPitchTests(unittest.TestCase):
    def test_duration_is_exact_active_work_excluding_terrain(self):
        pitch = parcours_util.get_parcours_pitch()
        self.assertEqual(parcours_util.PARCOURS_ACTIVE_MINUTES, 132)
        self.assertEqual(pitch["duration_label"], "2h12")
        self.assertEqual(pitch["steps"], 6)
        self.assertIn("2h12 de travail actif estimé", pitch["cta_label"])
        self.assertIn("hors test terrain", pitch["message_suffix"])

    def test_duration_format_does_not_round(self):
        for minutes, expected in [(0, "0 min"), (15, "15 min"), (60, "1h"), (65, "1h05"), (132, "2h12")]:
            with self.subTest(minutes=minutes):
                self.assertEqual(parcours_util._format_duration_label(minutes), expected)

    def test_existing_url_and_pitch_schema_remain_unchanged(self):
        with patch.object(parcours_util, "_resolve_case_hash", return_value="synthetic-hash"), \
                patch.object(parcours_util, "_parcours_base_url", return_value="https://example.invalid"):
            info = parcours_util.build_parcours_info("SYNTHETIC-UX")
        self.assertEqual(info["parcours_url"], "https://example.invalid/action-synthetic-hash.html")
        self.assertEqual(set(info), {
            "case_hash", "parcours_url", "steps", "duration_label", "cta_label", "message_suffix",
        })


class ParcoursTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = PARCOURS_ROOT / "pipeline" / "genere.py"
        if not source.is_file():
            raise unittest.SkipTest("Set PARCOURS_SOURCE_ROOT to the parcours repository for template tests")
        spec = importlib.util.spec_from_file_location("parcours_generator_ux", source)
        cls.generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.generator)
        cls.tpl = cls.generator.load_template()
        cls.gabarits = {
            path.stem: path.read_text(encoding="utf-8")
            for path in (PARCOURS_ROOT / "templates" / "etapes").glob("*.md")
        }

    def render(self, case):
        with patch.object(self.generator, "charge_base", side_effect=AssertionError("No workbook access")), \
                patch.object(self.generator.pd, "read_excel", side_effect=AssertionError("No workbook access")):
            return self.generator.render_page(case, "syntheticux", "synthetic", self.tpl, self.gabarits)

    def test_six_steps_in_order_duration_and_existing_backlink(self):
        for mode in ("outil", "no_code"):
            with self.subTest(mode=mode):
                html = self.render(synthetic_case(mode))
                page = PageParser(html)
                steps = [attrs["data-etape"] for _, attrs in page.elements if "data-etape" in attrs]
                self.assertEqual(steps, ["1", "2", "3", "4", "5", "6"])
                self.assertEqual(
                    [attrs["data-fin"] for _, attrs in page.elements if "data-fin" in attrs], steps,
                )
                active_minutes = 0
                for value, unit in re.findall(r'class="duree">(\d+) (min|h)</span>', html):
                    active_minutes += int(value) * (60 if unit == "h" else 1)
                self.assertEqual(active_minutes, parcours_util.PARCOURS_ACTIVE_MINUTES)
                self.assertIn("2h12 de travail actif estimé, hors test terrain de l'étape 5", html)
                self.assertIn('href="https://avouslia.fr"', html)
                self.assertIn('id="auto1" data-suivi', html)
                self.assertNotIn("&lt;p&gt;", html)

    def test_dynamic_case_text_and_prompt_values_remain_verbatim(self):
        case = synthetic_case()
        before = copy.deepcopy(case)
        page = PageParser(self.render(case))
        text = "".join(page.text)
        for field in ("cas_utilisation", "description_cas_utilisation", "domaine_label",
                      "intention", "effort", "sensibilite_donnees", "premiere_action_48h"):
            self.assertIn(case[field], text)
        for value in case["questions"] + case["prereqs"] + case["guardrails_liste"]:
            self.assertIn(value, text)
        prompt = page.pre[-1]
        self.assertEqual(prompt, self.generator.prompt_principal(case))
        self.assertIn(case["guardrails"], prompt)
        self.assertIn("Texte source : Je suis dirigeant.", prompt)
        self.assertEqual(case, before)

    def test_generic_role_is_completable_in_all_prompt_wrappers(self):
        page = PageParser(self.render(synthetic_case()))
        for prompt in page.pre:
            self.assertTrue(prompt.startswith("Mon rôle : [votre fonction ou rôle dans l'entreprise]."))
        self.assertNotIn("Je suis dirigeant d'une PME/TPE française.", "".join(page.text))
        self.assertNotIn("la version gratuite suffit", "".join(page.text))
        self.assertIn("assistant IA autorisé par votre organisation", "".join(page.text))

    def test_visible_shortcut_targets_existing_accessible_prompt(self):
        html = self.render(synthetic_case())
        page = PageParser(html)
        links = [attrs for tag, attrs in page.elements if tag == "a" and attrs.get("href") == "#prompt-demarrage"]
        self.assertEqual(len(links), 2)
        self.assertIn("tester-rapidement", links[0]["class"])
        self.assertLess(html.index(">Tester rapidement</a>"), html.index('data-etape="1"'))
        targets = [attrs for _, attrs in page.elements if attrs.get("id") == "prompt-demarrage"]
        self.assertEqual(len(targets), 1)
        self.assertEqual(targets[0]["tabindex"], "-1")
        self.assertEqual(targets[0]["aria-label"], "Votre prompt de démarrage")
        self.assertIn("scroll-margin-top:90px", html)

    @unittest.skipUnless(shutil.which("node"), "Node required for DOM event-handler checks")
    def test_prompt_navigation_on_click_hashchange_and_initial_fragment(self):
        html = self.render(synthetic_case())
        script = re.search(r"<script>(.*?)</script>", html, re.S).group(1)
        harness = r"""
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = SCRIPT;
for (const initialHash of ['', '#prompt-demarrage']) {
  const accordion = {open: false};
  const links = [{}, {}], events = {};
  let focused = 0, scrolled = 0;
  const target = {
    closest: selector => {assert.equal(selector, 'details'); return accordion;},
    focus: options => {assert.equal(accordion.open, true); assert.equal(options.preventScroll, true); focused++;},
    scrollIntoView: options => {assert.equal(options.block, 'start'); scrolled++;}
  };
  links.forEach(link => link.addEventListener = (name, handler) => link[name] = handler);
  const window = {location: {hash: initialHash}, addEventListener: (name, handler) => events[name] = handler};
  const document = {
    querySelectorAll: selector => selector === 'a[href="#prompt-demarrage"]' ? links : [],
    querySelector: () => null,
    getElementById: id => id === 'prompt-demarrage' ? target : {style: {}}
  };
  vm.runInNewContext(source, {window, document, localStorage: {getItem: () => '{}'}});
  assert.equal(accordion.open, initialHash === '#prompt-demarrage');
  for (const link of links) {
    accordion.open = false;
    link.click();
    assert.equal(accordion.open, true);
  }
  accordion.open = false;
  window.location.hash = '#prompt-demarrage';
  events.hashchange();
  assert.equal(accordion.open, true);
  assert.equal(focused, scrolled);
  assert.equal(focused, initialHash ? 4 : 3);
  accordion.open = false;
  window.location.hash = '#other';
  events.hashchange();
  assert.equal(accordion.open, false);
}
"""
        result = subprocess.run(
            ["node", "-e", harness.replace("SCRIPT", json.dumps(script))],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
