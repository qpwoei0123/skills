import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from compute_normalize_targets import build_targets  # noqa: E402


class ComputeNormalizeTargetsTest(unittest.TestCase):
    def write_skill(self, root: Path, category: str, name: str) -> None:
        skill_md = root / "skills" / category / name / "SKILL.md"
        skill_md.parent.mkdir(parents=True, exist_ok=True)
        skill_md.write_text(f"---\nname: {name}\n---\n", encoding="utf-8")

    def test_only_changed_autofixable_skills_become_targets(self):
        payload = {
            "skills": [
                {
                    "name": "alpha",
                    "errors": [
                        {
                            "code": "missing_readme",
                            "message": "필수 파일 누락: README.md",
                            "autofixable": True,
                        }
                    ],
                    "warnings": [],
                },
                {
                    "name": "beta",
                    "errors": [
                        {
                            "code": "missing_license",
                            "message": "frontmatter 필수 키 누락 또는 빈 값: license",
                            "autofixable": False,
                        }
                    ],
                    "warnings": [],
                },
            ]
        }

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_skill(root, "데일리함", "alpha")
            self.write_skill(root, "살짝무거움", "beta")

            result = build_targets(
                validate_payload=payload,
                changed_files=[
                    "skills/데일리함/alpha/SKILL.md",
                    "skills/살짝무거움/beta/SKILL.md",
                    "README.md",
                ],
                base_branch="main",
                trigger_sha="abcdef1234567890",
                repo_root=root,
            )

        self.assertEqual(len(result["include"]), 1)
        target = result["include"][0]
        self.assertEqual(target["skill"], "alpha")
        self.assertEqual(target["branch"], "codex/normalize-alpha")


if __name__ == "__main__":
    unittest.main()
