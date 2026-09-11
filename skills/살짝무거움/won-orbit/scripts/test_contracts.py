import re
import unittest
from pathlib import Path


ORBIT_ROOT = Path(__file__).resolve().parents[1]
DOC_PATHS = [
    ORBIT_ROOT / "SKILL.md",
    ORBIT_ROOT / "agents" / "orchestrator.md",
    ORBIT_ROOT / "references" / "output-templates.md",
    ORBIT_ROOT / "README.md",
]

CONCRETE_FINGERPRINT_RE = re.compile(
    r"pipeline:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+:[A-Z]+:[A-Za-z0-9_-]+"
)
CURRENT_FINGERPRINT_RE = re.compile(
    r"^pipeline:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+:[A-Z]+:f-[0-9a-f]{8}$"
)
LEGACY_SEQUENCE_ID_RE = re.compile(r"(?<![A-Za-z0-9_-])E\d+(?![A-Za-z0-9_-])")


class OrbitContractDocsTest(unittest.TestCase):
    def test_concrete_fingerprint_examples_use_hashed_finding_ids(self):
        failures = []
        for path in DOC_PATHS:
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for match in CONCRETE_FINGERPRINT_RE.finditer(line):
                    fingerprint = match.group(0)
                    if not CURRENT_FINGERPRINT_RE.match(fingerprint):
                        failures.append(f"{path.relative_to(ORBIT_ROOT)}:{lineno}: {fingerprint}")

        self.assertEqual([], failures)

    def test_orbit_fingerprint_mentions_use_html_comment_footer(self):
        failures = []
        for path in DOC_PATHS:
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if "orbit-fingerprint:" not in line:
                    continue
                if "<!-- orbit-fingerprint:" not in line or "-->" not in line:
                    failures.append(f"{path.relative_to(ORBIT_ROOT)}:{lineno}: {line}")

        self.assertEqual([], failures)

    def test_legacy_sequence_ids_do_not_reappear_in_contract_docs(self):
        failures = []
        for path in DOC_PATHS:
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if LEGACY_SEQUENCE_ID_RE.search(line):
                    failures.append(f"{path.relative_to(ORBIT_ROOT)}:{lineno}: {line}")

        self.assertEqual([], failures)

    def test_migration_docs_mention_closed_and_suppressed_aliases(self):
        for path in [ORBIT_ROOT / "SKILL.md", ORBIT_ROOT / "agents" / "orchestrator.md"]:
            with self.subTest(path=path.relative_to(ORBIT_ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertIn("status == \"open\"", text)
                self.assertIn("status == \"closed\"", text)
                self.assertIn("status == \"suppressed\"", text)
                self.assertIn("--legacy-fingerprint", text)


if __name__ == "__main__":
    unittest.main()
