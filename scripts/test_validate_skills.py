import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from skill_repo_lib import build_json_payload, validate_skill  # noqa: E402


class ValidateSkillsTest(unittest.TestCase):
    def write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_json_payload_marks_autofixable_errors(self):
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

            report = validate_skill(skill_dir)
            payload = build_json_payload([report])

        error_map = {error["code"]: error for error in payload["skills"][0]["errors"]}
        self.assertTrue(error_map["missing_readme"]["autofixable"])
        self.assertTrue(error_map["missing_changelog"]["autofixable"])
        self.assertTrue(
            error_map["metadata_version_missing_with_legacy_version"]["autofixable"]
        )

    def test_invalid_name_is_manual_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "wild-skill"
            self.write(
                skill_dir / "SKILL.md",
                "\n".join(
                    [
                        "---",
                        "name: another-name",
                        "license: Apache-2.0",
                        "metadata:",
                        "  version: 0.1.0",
                        "description: 테스트 스킬",
                        "---",
                        "",
                        "# Wild Skill",
                    ]
                ),
            )
            self.write(skill_dir / "README.md", "# Wild Skill\n\n`version: 0.1.0`\n")
            self.write(skill_dir / "CHANGELOG.md", "# Changelog\n\n## 0.1.0\n")

            report = validate_skill(skill_dir)

        invalid_name = next(error for error in report.errors if error.code == "invalid_name")
        self.assertFalse(invalid_name.autofixable)


if __name__ == "__main__":
    unittest.main()
