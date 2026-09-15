import unittest

from scripts.publish_accessibility_pages import REPLACEMENTS, replace_owned


class AccessibilityOverlayTests(unittest.TestCase):
    def setUp(self):
        self.source = "\n".join(before for before, _ in REPLACEMENTS)

    def test_exact_owned_round_trip_preserves_arbitrary_source_and_prompt_bytes(self):
        original = self.source + '\n<pre>SOURCE &lt;A&gt;\n100 % exemple, pas un gain</pre>'
        changed = replace_owned(original)
        self.assertIn('<pre>SOURCE &lt;A&gt;\n100 % exemple, pas un gain</pre>', changed)
        for before, after in reversed(REPLACEMENTS):
            changed = changed.replace(after, before, 1)
        self.assertEqual(changed, original)

    def test_ambiguous_missing_and_already_patched_surfaces_fail_closed(self):
        for source in (self.source + REPLACEMENTS[1][0],
                       self.source.replace(REPLACEMENTS[1][0], ""),
                       replace_owned(self.source)):
            with self.subTest(source=source[:20]), self.assertRaises(ValueError):
                replace_owned(source)

    def test_focus_ring_is_inset_and_copy_status_exists_before_updates(self):
        result = replace_owned(self.source)
        self.assertIn("summary:focus-visible{outline-offset:-3px}", result)
        self.assertIn('role="status" aria-atomic="true"', result)
        self.assertLess(result.index('id="copie-statut"'), result.index("statutCopie.textContent"))
