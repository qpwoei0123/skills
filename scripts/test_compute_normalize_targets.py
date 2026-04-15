import sys
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from compute_normalize_targets import build_targets  # noqa: E402
from skill_repo_lib import repo_root_from_script  # noqa: E402


class ComputeNormalizeTargetsTest(unittest.TestCase):
    def setUp(self):
        self.repo_root = repo_root_from_script(Path(__file__))

    def test_only_changed_autofixable_skills_become_targets(self):
        payload = {
            "skills": [
                {
                    "name": "ghostwriter",
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
                    "name": "orbit",
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

        result = build_targets(
            validate_payload=payload,
            changed_files=["ghostwriter/SKILL.md", "orbit/SKILL.md", "README.md"],
            source_branch="feature/wild-skill",
            repo_root=self.repo_root,
        )

        self.assertEqual(len(result["include"]), 1)
        target = result["include"][0]
        self.assertEqual(target["skill"], "ghostwriter")
        self.assertEqual(
            target["branch"],
            "codex/normalize-ghostwriter-for-feature-wild-skill",
        )


if __name__ == "__main__":
    unittest.main()
