import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from normalize_skill import normalize_skill_directory  # noqa: E402
from skill_repo_lib import repo_root_from_script, validate_skill  # noqa: E402


class NormalizeSkillTest(unittest.TestCase):
    def setUp(self):
        self.repo_root = repo_root_from_script(Path(__file__))

    def write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_check_mode_reports_changes_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "wild-skill"
            self.write(
                skill_dir / "SKILL.md",
                "\n".join(
                    [
                        "---",
                        "name: wild-skill",
                        "license: Apache-2.0",
                        "version: 0.1.0",
                        "description: 테스트 스킬",
                        "---",
                        "",
                        "# Wild Skill",
                    ]
                ),
            )

            result = normalize_skill_directory(skill_dir, repo_root=self.repo_root, write=False)

            self.assertFalse(result.has_blockers)
            self.assertTrue(result.applied_changes)
            self.assertFalse((skill_dir / "README.md").exists())
            self.assertIn("version: 0.1.0", (skill_dir / "SKILL.md").read_text(encoding="utf-8"))

    def test_write_mode_migrates_version_and_creates_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "wild-skill"
            self.write(
                skill_dir / "SKILL.md",
                "\n".join(
                    [
                        "---",
                        "name: wild-skill",
                        "license: Apache-2.0",
                        "version: 0.1.0",
                        "description: 테스트 스킬",
                        "---",
                        "",
                        "# Wild Skill",
                    ]
                ),
            )

            result = normalize_skill_directory(skill_dir, repo_root=self.repo_root, write=True)
            report = validate_skill(skill_dir)

            self.assertFalse(result.has_blockers)
            self.assertFalse(result.remaining_errors)
            self.assertFalse(report.errors)

            skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("metadata:", skill_text)
            self.assertIn("  version: 0.1.0", skill_text)
            self.assertNotIn("\nversion: 0.1.0\n", skill_text)
            self.assertTrue((skill_dir / "README.md").exists())
            self.assertTrue((skill_dir / "CHANGELOG.md").exists())

    def test_manual_blockers_stop_normalization(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "wild-skill"
            self.write(
                skill_dir / "SKILL.md",
                "\n".join(
                    [
                        "---",
                        "name: wild-skill",
                        "version: 0.1.0",
                        "description: 테스트 스킬",
                        "---",
                        "",
                        "# Wild Skill",
                    ]
                ),
            )

            result = normalize_skill_directory(skill_dir, repo_root=self.repo_root, write=True)

            blocker_codes = {blocker.code for blocker in result.blockers}
            self.assertIn("missing_license", blocker_codes)
            self.assertFalse((skill_dir / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
