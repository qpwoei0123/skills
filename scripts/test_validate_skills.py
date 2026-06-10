import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from skill_repo_lib import build_json_payload, validate_root_readme, validate_skill  # noqa: E402


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

    def test_description_version_prefix_is_checked_and_autofixable(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "wild-skill"
            self.write(
                skill_dir / "SKILL.md",
                "\n".join(
                    [
                        "---",
                        "name: wild-skill",
                        "license: Apache-2.0",
                        "metadata:",
                        "  version: 0.2.0",
                        "description: (v0.1.0) 테스트 스킬",
                        "---",
                        "",
                        "# Wild Skill",
                    ]
                ),
            )
            self.write(skill_dir / "README.md", "# Wild Skill\n\n`version: 0.2.0`\n\n## Quick Start\n\n## Structure\n\n## Test\n")
            self.write(skill_dir / "CHANGELOG.md", "# Changelog\n\n## 0.2.0\n")

            report = validate_skill(skill_dir)

        prefix_error = next(
            error for error in report.errors if error.code == "description_version_prefix_mismatch"
        )
        self.assertIn("0.1.0", prefix_error.message)
        self.assertTrue(prefix_error.autofixable)

    def test_root_readme_list_must_match_skill_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(
                root / "README.md",
                "\n".join(
                    [
                        "# skills",
                        "",
                        "## Accepted Skills",
                        "",
                        "- `alpha`: 스킬 A",
                        "- `ghost 👻`: 삭제된 스킬",
                        "",
                        "## Next Step",
                    ]
                ),
            )

            report = validate_root_readme(root, ["alpha", "beta"])

        codes = {(error.code, error.message) for error in report.errors}
        self.assertIn(
            ("root_readme_skill_unlisted", "Accepted Skills 목록에 없는 스킬 디렉터리: beta"),
            codes,
        )
        self.assertIn(
            ("root_readme_stale_skill", "디렉터리가 없는 스킬이 목록에 남아 있음: ghost"),
            codes,
        )


if __name__ == "__main__":
    unittest.main()
