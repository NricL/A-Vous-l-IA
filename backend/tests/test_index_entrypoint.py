import os
from pathlib import Path
import shutil
import subprocess
import unittest


ENTRYPOINT = Path(__file__).resolve().parents[1] / "entrypoint.sh"
BASH = shutil.which("bash")
if not BASH and os.name == "nt":
    installed = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git" / "bin" / "bash.exe"
    if installed.is_file():
        BASH = str(installed)


@unittest.skipUnless(BASH, "Bash is required to exercise the container entrypoint")
class IndexEntrypointTests(unittest.TestCase):
    def run_entrypoint(self, *, index_path="/synthetic/catalogue.xlsx", count="0", count_exit="0", write_exit="0"):
        env = os.environ.copy()
        env.update(TEST_COUNT=count, TEST_COUNT_EXIT=count_exit, TEST_WRITE_EXIT=write_exit)
        env.pop("INDEX_PATH", None)
        if index_path is not None:
            env["INDEX_PATH"] = index_path
        script = r'''
python() {
  if [ "$1" = "-c" ]; then
    printf '%s\n' "$TEST_COUNT"
    return "$TEST_COUNT_EXIT"
  fi
  printf 'INDEX_COMMAND:'
  printf '<%s>' "$@"
  printf '\n'
  return "$TEST_WRITE_EXIT"
}
export -f python
"$BASH" ./entrypoint.sh "$BASH" -c 'printf "APP_STARTED\n"'
'''
        return subprocess.run(
            [BASH, "-c", script],
            cwd=ENTRYPOINT.parent,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )

    def test_without_source_starts_without_index_access(self):
        result = self.run_entrypoint(index_path=None, count_exit="9")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("APP_STARTED", result.stdout)
        self.assertNotIn("INDEX_COMMAND", result.stdout)

    def test_existing_index_is_not_rebuilt(self):
        result = self.run_entrypoint(count="42")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("INDEX_COMMAND", result.stdout)
        self.assertIn("APP_STARTED", result.stdout)

    def test_unreadable_index_does_not_start_or_attempt_clear(self):
        result = self.run_entrypoint(count_exit="4")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("INDEX_COMMAND", result.stdout)
        self.assertNotIn("APP_STARTED", result.stdout)

    def test_invalid_count_is_not_treated_as_empty(self):
        for count in ["", "-1", "0\nwarning", "unknown"]:
            with self.subTest(count=count):
                result = self.run_entrypoint(count=count)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("INDEX_COMMAND", result.stdout)
                self.assertNotIn("APP_STARTED", result.stdout)

    def test_empty_index_uses_non_destructive_requirement_and_quoted_path(self):
        result = self.run_entrypoint(index_path="/synthetic/catalogue with spaces.xlsx")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("<--require-empty></synthetic/catalogue with spaces.xlsx>", result.stdout)
        self.assertNotIn("--clear", result.stdout)
        self.assertIn("APP_STARTED", result.stdout)

    def test_failed_indexing_does_not_report_success_or_start_app(self):
        result = self.run_entrypoint(write_exit="7")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("INDEX_COMMAND", result.stdout)
        self.assertNotIn("Indexation terminée", result.stdout)
        self.assertNotIn("APP_STARTED", result.stdout)


if __name__ == "__main__":
    unittest.main()
