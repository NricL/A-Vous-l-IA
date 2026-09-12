from pathlib import Path
import unittest

import yaml

from test_parcours_ux import PARCOURS_ROOT


class ParcoursPublicationGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(PARCOURS_ROOT) / ".github" / "workflows" / "publish.yml"
        if not path.is_file():
            raise unittest.SkipTest("Set PARCOURS_SOURCE_ROOT for the separate publication workflow")
        cls.workflow = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        cls.job = cls.workflow["jobs"]["build-deploy"]
        cls.steps = cls.job["steps"]

    def test_publication_is_not_triggered_by_source_push(self):
        self.assertEqual(set(self.workflow["on"]), {"workflow_dispatch"})
        self.assertIn("inputs.publish_authorized", self.job["if"])
        self.assertEqual(self.job["environment"], "parcours-publication")
        fields = self.workflow["on"]["workflow_dispatch"]["inputs"]
        self.assertEqual(fields["publish_authorized"]["default"], "false")
        self.assertEqual(fields["publish_authorized"]["type"], "boolean")
        for field in ("workbook", "mapping"):
            self.assertEqual(fields[field]["required"], "true")

    def test_generation_uses_explicit_sources_and_never_development_hashes(self):
        generate = next(s["run"] for s in self.steps if "--output-dir dist" in s.get("run", ""))
        for flag in ("--workbook", "--sheet Sheet1", "--mapping", "--app-url"):
            self.assertIn(flag, generate)
        self.assertNotIn("--development", generate)
        self.assertNotIn("--replace-dist", generate)
        self.assertNotIn("AVOULIA_SALT", str(self.workflow))

    def test_mapping_removed_before_web_upload_and_never_uploaded_as_artifact(self):
        gate = next(i for i, s in enumerate(self.steps) if "mapping.unlink()" in s.get("run", ""))
        upload = next(i for i, s in enumerate(self.steps) if s.get("uses", "").startswith("Azure/static-web-apps-deploy"))
        self.assertLess(gate, upload)
        self.assertNotIn("actions/upload-artifact", str(self.workflow))
        self.assertEqual(self.steps[upload]["with"]["app_location"], "dist")
        script = self.steps[gate]["run"]
        self.assertIn('root / "mapping_uc_hash.csv"', script)
        self.assertIn('{".html", ".txt"}', script)

    def test_historical_mapping_difference_blocks_whole_site_replacement(self):
        script = next(s["run"] for s in self.steps if "set(mapping)" in s.get("run", ""))
        self.assertIn('set(frame["use_case_id"]) != set(mapping)', script)
        self.assertIn('Path("dist").exists()', script)
        self.assertIn("raise SystemExit", script)
        self.assertIn('charge_base(sources[0], "Sheet1")', script)


if __name__ == "__main__":
    unittest.main()
