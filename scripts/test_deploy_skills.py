import io
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import deploy_skills as MODULE  # noqa: E402


class DeploySkillsTest(unittest.TestCase):
    def write_valid_skill(self, skill_dir: Path, marker: str) -> None:
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    f"name: {skill_dir.name}",
                    "license: Apache-2.0",
                    "metadata:",
                    "  version: 0.1.0",
                    "description: (v0.1.0) 테스트 스킬",
                    "---",
                    "",
                    f"# {skill_dir.name}",
                ]
            ),
            encoding="utf-8",
        )
        (skill_dir / "README.md").write_text(
            f"# {skill_dir.name}\n\n`version: 0.1.0`\n\n{marker}\n\n"
            "## Quick Start\n\n## Structure\n\n## Test\n",
            encoding="utf-8",
        )
        (skill_dir / "CHANGELOG.md").write_text(
            "# Changelog\n\n## 0.1.0\n",
            encoding="utf-8",
        )

    def run_check(self, repo_root: Path, target: Path) -> tuple[int, str]:
        output = io.StringIO()
        with patch.object(MODULE, "repo_root_from_script", return_value=repo_root):
            with patch("sys.argv", ["deploy_skills.py", "--target", str(target), "--check"]):
                with redirect_stdout(output):
                    result = MODULE.main()
        return result, output.getvalue()

    def test_check_detects_content_drift_with_same_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "repo" / "skills" / "데일리함" / "alpha"
            target = root / "deployed"
            deployed = target / "alpha"
            self.write_valid_skill(source, "repo content")
            shutil.copytree(source, deployed)
            (deployed / "__pycache__").mkdir()
            (deployed / "__pycache__" / "helper.pyc").write_bytes(b"compiled")
            (deployed / ".DS_Store").write_bytes(b"finder")
            (deployed / "node_modules" / "package").mkdir(parents=True)
            (deployed / "node_modules" / "package" / "index.js").write_text(
                "generated dependency",
                encoding="utf-8",
            )

            result, output = self.run_check(root / "repo", target)
            self.assertEqual(result, 0)
            self.assertIn("내용 일치", output)

            (deployed / "README.md").write_text(
                (deployed / "README.md").read_text(encoding="utf-8") + "drift\n",
                encoding="utf-8",
            )
            result, output = self.run_check(root / "repo", target)

        self.assertEqual(result, 1)
        self.assertIn("배포본 0.1.0 = 레포 0.1.0; 내용 drift", output)

    def test_staging_validation_fails_before_existing_deployment_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source" / "alpha"
            target = root / "deployed"
            deployed = target / "alpha"
            self.write_valid_skill(source, "new content")
            self.write_valid_skill(deployed, "old content")
            original_copytree = shutil.copytree

            def copy_without_readme(src, dst, *args, **kwargs):
                result = original_copytree(src, dst, *args, **kwargs)
                (Path(dst) / "README.md").unlink()
                return result

            with patch.object(MODULE.shutil, "copytree", side_effect=copy_without_readme):
                with self.assertRaises(MODULE.DeploymentError):
                    MODULE.prepare_deployments([source], target)

            deployed_readme = (deployed / "README.md").read_text(encoding="utf-8")

        self.assertIn("old content", deployed_readme)

    def test_swap_failure_rolls_back_existing_deployment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source" / "alpha"
            target = root / "deployed"
            deployed = target / "alpha"
            self.write_valid_skill(source, "new content")
            self.write_valid_skill(deployed, "old content")
            staging_root, plans = MODULE.prepare_deployments([source], target)
            original_replace = os.replace
            calls = 0

            def fail_activation(src, dst):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("activation failed")
                return original_replace(src, dst)

            try:
                with patch.object(MODULE.os, "replace", side_effect=fail_activation):
                    with self.assertRaises(MODULE.DeploymentError):
                        MODULE.apply_deployments(plans)
                deployed_readme = (deployed / "README.md").read_text(encoding="utf-8")
                replace_call_count = calls
            finally:
                shutil.rmtree(staging_root, ignore_errors=True)

        self.assertIn("old content", deployed_readme)
        self.assertEqual(replace_call_count, 3)

    def test_swap_failure_restores_relative_symlink_deployment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source" / "alpha"
            previous = root / "old" / "alpha"
            target = root / "deployed"
            deployed = target / "alpha"
            self.write_valid_skill(source, "new content")
            self.write_valid_skill(previous, "old content")
            target.mkdir()
            deployed.symlink_to(Path("../old/alpha"), target_is_directory=True)
            staging_root, plans = MODULE.prepare_deployments([source], target)
            original_replace = os.replace
            calls = 0

            def fail_activation(src, dst):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("activation failed")
                return original_replace(src, dst)

            try:
                with patch.object(MODULE.os, "replace", side_effect=fail_activation):
                    with self.assertRaises(MODULE.DeploymentError):
                        MODULE.apply_deployments(plans)
                restored = deployed.is_symlink() and deployed.resolve() == previous.resolve()
            finally:
                shutil.rmtree(staging_root, ignore_errors=True)

        self.assertTrue(restored)

    def test_corrupt_existing_version_does_not_block_replacement(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_root = root / "repo"
            source = repo_root / "skills" / "데일리함" / "alpha"
            target = root / "deployed"
            deployed = target / "alpha"
            self.write_valid_skill(source, "new content")
            deployed.mkdir(parents=True)
            (deployed / "SKILL.md").write_text("broken", encoding="utf-8")

            output = io.StringIO()
            with patch.object(MODULE, "repo_root_from_script", return_value=repo_root):
                with patch("sys.argv", ["deploy_skills.py", "--target", str(target)]):
                    with redirect_stdout(output):
                        result = MODULE.main()

            deployed_readme = (deployed / "README.md").read_text(encoding="utf-8")

        self.assertEqual(result, 0)
        self.assertIn("확인 불가 → 0.1.0", output.getvalue())
        self.assertIn("new content", deployed_readme)

    def test_later_swap_failure_rolls_back_prior_deployments(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "deployed"
            sources = [root / "source" / name for name in ("alpha", "beta")]
            for source in sources:
                self.write_valid_skill(source, f"new {source.name}")
                self.write_valid_skill(target / source.name, f"old {source.name}")

            staging_root, plans = MODULE.prepare_deployments(sources, target)
            original_replace = os.replace
            calls = 0

            def fail_second_activation(src, dst):
                nonlocal calls
                calls += 1
                if calls == 4:
                    raise OSError("second activation failed")
                return original_replace(src, dst)

            try:
                with patch.object(MODULE.os, "replace", side_effect=fail_second_activation):
                    with self.assertRaises(MODULE.DeploymentError):
                        MODULE.apply_deployments(plans)
                deployed_contents = {
                    name: (target / name / "README.md").read_text(encoding="utf-8")
                    for name in ("alpha", "beta")
                }
            finally:
                shutil.rmtree(staging_root, ignore_errors=True)

        self.assertIn("old alpha", deployed_contents["alpha"])
        self.assertIn("old beta", deployed_contents["beta"])

    def test_valid_staging_is_swapped_into_place(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source" / "alpha"
            target = root / "deployed"
            deployed = target / "alpha"
            self.write_valid_skill(source, "new content")
            self.write_valid_skill(deployed, "old content")
            (source / "__pycache__").mkdir()
            (source / "__pycache__" / "helper.pyc").write_bytes(b"compiled")
            (source / ".DS_Store").write_bytes(b"finder")
            (source / "node_modules" / "package").mkdir(parents=True)
            (source / "node_modules" / "package" / "index.js").write_text(
                "generated dependency",
                encoding="utf-8",
            )
            staging_root, plans = MODULE.prepare_deployments([source], target)
            try:
                MODULE.apply_deployments(plans)
                deployed_readme = (deployed / "README.md").read_text(encoding="utf-8")
                transient_paths = [
                    deployed / "__pycache__",
                    deployed / ".DS_Store",
                    deployed / "node_modules",
                ]
            finally:
                shutil.rmtree(staging_root, ignore_errors=True)

        self.assertIn("new content", deployed_readme)
        self.assertFalse(any(path.exists() for path in transient_paths))


if __name__ == "__main__":
    unittest.main()
