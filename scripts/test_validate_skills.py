import json
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

    def write_valid_skill(self, skill_dir: Path, description: str = "(v0.1.0) 테스트 스킬") -> None:
        self.write(
            skill_dir / "SKILL.md",
            "\n".join(
                [
                    "---",
                    f"name: {skill_dir.name}",
                    "license: Apache-2.0",
                    "metadata:",
                    "  version: 0.1.0",
                    f"description: {description}",
                    "---",
                    "",
                    f"# {skill_dir.name}",
                ]
            ),
        )
        self.write(
            skill_dir / "README.md",
            f"# {skill_dir.name}\n\n`version: 0.1.0`\n\n## Quick Start\n\n## Structure\n\n## Test\n",
        )
        self.write(skill_dir / "CHANGELOG.md", "# Changelog\n\n## 0.1.0\n")

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

    def test_block_scalar_description_is_rejected_as_manual_error(self):
        for indicator in ("|", ">-", "|2 # 들여쓰기 지정"):
            with self.subTest(indicator=indicator), tempfile.TemporaryDirectory() as tmp:
                skill_dir = Path(tmp) / "wild-skill"
                self.write_valid_skill(
                    skill_dir,
                    f"{indicator}\n  (v0.1.0) 여러 줄 설명",
                )

                report = validate_skill(skill_dir)

                error = next(
                    error
                    for error in report.errors
                    if error.code == "description_must_be_single_line"
                )
                self.assertFalse(error.autofixable)

    def test_trigger_eval_contract(self):
        cases = [
            ("invalid-json", "{", {"trigger_eval_invalid_json"}),
            (
                "invalid-fields",
                json.dumps(
                    [
                        {
                            "query": 1,
                            "should_trigger": "yes",
                            "expected_behavior": 3,
                        }
                    ]
                ),
                {
                    "trigger_eval_invalid_query",
                    "trigger_eval_invalid_should_trigger",
                    "trigger_eval_invalid_expected_behavior",
                },
            ),
            (
                "unbalanced",
                json.dumps(
                    [
                        {"query": "실행해줘", "should_trigger": True},
                        {"query": "이것도 실행해줘", "should_trigger": True},
                    ]
                ),
                {"trigger_eval_unbalanced"},
            ),
            (
                "balanced",
                json.dumps(
                    [
                        {"query": "실행해줘", "should_trigger": True},
                        {"query": "다른 작업", "should_trigger": False},
                    ]
                ),
                set(),
            ),
        ]

        for name, payload, expected_codes in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                skill_dir = Path(tmp) / "wild-skill"
                self.write_valid_skill(skill_dir)
                self.write(skill_dir / "evals" / "trigger-eval.json", payload)

                report = validate_skill(skill_dir)
                codes = {
                    error.code
                    for error in report.errors
                    if error.code.startswith("trigger_eval_")
                }

                self.assertEqual(codes, expected_codes)

    def test_openai_manifest_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "wild-skill"
            self.write_valid_skill(skill_dir)
            self.write(
                skill_dir / "agents" / "openai.yaml",
                "\n".join(
                    [
                        "interface:",
                        '  display_name: ""',
                        '  short_description: "너무 짧음"',
                        '  default_prompt: "호출 이름이 없는 기본 프롬프트"',
                    ]
                ),
            )

            report = validate_skill(skill_dir)

        codes = {error.code for error in report.errors}
        self.assertIn("openai_yaml_missing_field", codes)
        self.assertIn("openai_yaml_short_description_length", codes)
        self.assertIn("openai_yaml_default_prompt_trigger", codes)

    def test_openai_manifest_accepts_inline_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "wild-skill"
            self.write_valid_skill(skill_dir)
            self.write(
                skill_dir / "agents" / "openai.yaml",
                "\n".join(
                    [
                        "interface:",
                        '  display_name: "Wild Skill" # 표시 이름',
                        '  short_description: "반복 작업을 안전하고 일관된 절차로 처리하는 스킬입니다" # 길이에서 제외할 주석',
                        '  default_prompt: "$wild-skill로 이 작업을 처리해 주세요." # 호출 예시',
                    ]
                ),
            )

            report = validate_skill(skill_dir)

        self.assertFalse(
            [error for error in report.errors if error.code.startswith("openai_yaml_")]
        )

    def test_openai_manifest_rejects_fields_nested_below_interface_child(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "wild-skill"
            self.write_valid_skill(skill_dir)
            self.write(
                skill_dir / "agents" / "openai.yaml",
                "\n".join(
                    [
                        "interface:",
                        "  metadata:",
                        '    display_name: "Wild Skill"',
                        '    short_description: "반복 작업을 안전하고 일관된 절차로 처리하는 스킬입니다"',
                        '    default_prompt: "$wild-skill로 이 작업을 처리해 주세요."',
                    ]
                ),
            )

            report = validate_skill(skill_dir)

        missing = [error for error in report.errors if error.code == "openai_yaml_missing_field"]
        self.assertEqual(len(missing), 3)

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
