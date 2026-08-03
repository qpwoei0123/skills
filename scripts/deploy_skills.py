#!/usr/bin/env python3
"""Validate 통과한 정식 스킬을 로컬 배포 디렉터리(~/.agents/skills)로 동기화한다."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from skill_repo_lib import (
    discover_skills,
    metadata_version,
    parse_frontmatter,
    repo_root_from_script,
    validate_skill,
)


TRANSIENT_NAMES = {".DS_Store", "__pycache__", "node_modules"}


class DeploymentError(RuntimeError):
    def __init__(self, message: str, preserve_staging: bool = False):
        super().__init__(message)
        self.preserve_staging = preserve_staging


@dataclass(frozen=True)
class DeploymentPlan:
    name: str
    staged: Path
    deployed: Path
    backup: Path


def skill_version(skill_dir: Path) -> str:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    return metadata_version(parse_frontmatter(text))


def deployed_version(skill_dir: Path) -> str:
    if not (skill_dir / "SKILL.md").exists():
        return "없음"
    try:
        return skill_version(skill_dir) or "확인 불가"
    except (OSError, ValueError):
        return "확인 불가"


def directory_manifest(root: Path) -> dict[str, tuple[str, str]]:
    manifest: dict[str, tuple[str, str]] = {}
    if not root.is_dir():
        return manifest

    for current, dirnames, filenames in os.walk(root):
        current_path = Path(current)
        deployable_dirs = []
        for dirname in sorted(dirnames):
            if dirname in TRANSIENT_NAMES:
                continue
            path = current_path / dirname
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                manifest[relative] = ("link", os.readlink(path))
            else:
                manifest[relative] = ("dir", "")
                deployable_dirs.append(dirname)
        dirnames[:] = deployable_dirs

        for filename in sorted(filenames):
            path = current_path / filename
            if filename in TRANSIENT_NAMES or path.suffix == ".pyc":
                continue
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                manifest[relative] = ("link", os.readlink(path))
            else:
                manifest[relative] = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
    return manifest


def contents_match(source: Path, deployed: Path) -> bool:
    return deployed.is_dir() and directory_manifest(source) == directory_manifest(deployed)


def prepare_deployments(
    skill_dirs: list[Path],
    target_root: Path,
) -> tuple[Path, list[DeploymentPlan]]:
    target_root.mkdir(parents=True, exist_ok=True)
    staging_root = Path(tempfile.mkdtemp(prefix=".deploy-staging-", dir=target_root))
    plans: list[DeploymentPlan] = []

    try:
        for skill_dir in skill_dirs:
            name = skill_dir.name
            staged = staging_root / "next" / name
            staged.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(
                skill_dir,
                staged,
                symlinks=True,
                ignore=shutil.ignore_patterns(*TRANSIENT_NAMES, "*.pyc"),
            )

            report = validate_skill(staged)
            if report.errors:
                codes = ", ".join(error.code for error in report.errors)
                raise DeploymentError(f"{name} staging 검증 실패: {codes}")
            if not contents_match(skill_dir, staged):
                raise DeploymentError(f"{name} staging 내용이 원본과 다릅니다.")

            plans.append(
                DeploymentPlan(
                    name=name,
                    staged=staged,
                    deployed=target_root / name,
                    backup=staging_root / "previous" / name,
                )
            )
    except DeploymentError:
        shutil.rmtree(staging_root, ignore_errors=True)
        raise
    except OSError as error:
        shutil.rmtree(staging_root, ignore_errors=True)
        raise DeploymentError(f"staging 생성 실패: {error}") from error

    return staging_root, plans


def apply_deployments(plans: list[DeploymentPlan]) -> None:
    swapped: list[tuple[DeploymentPlan, bool]] = []

    try:
        for plan in plans:
            had_previous = os.path.lexists(plan.deployed)
            if had_previous:
                plan.backup.parent.mkdir(parents=True, exist_ok=True)
                os.replace(plan.deployed, plan.backup)
            swapped.append((plan, had_previous))
            os.replace(plan.staged, plan.deployed)
    except OSError as error:
        rollback_errors = []
        for plan, had_previous in reversed(swapped):
            try:
                if os.path.lexists(plan.deployed):
                    os.replace(plan.deployed, plan.staged)
                if had_previous and os.path.lexists(plan.backup):
                    os.replace(plan.backup, plan.deployed)
            except OSError as rollback_error:
                rollback_errors.append(f"{plan.name}: {rollback_error}")

        if rollback_errors:
            raise DeploymentError(
                "swap 실패 후 rollback도 완료하지 못했습니다: " + "; ".join(rollback_errors),
                preserve_staging=True,
            ) from error
        raise DeploymentError(f"swap 실패로 기존 배포본을 복구했습니다: {error}") from error


def main() -> int:
    parser = argparse.ArgumentParser(description="레포 스킬을 배포 디렉터리로 동기화합니다.")
    parser.add_argument(
        "--target",
        type=Path,
        default=Path.home() / ".agents" / "skills",
        help="배포 디렉터리 (기본: ~/.agents/skills)",
    )
    parser.add_argument(
        "--skill",
        action="append",
        dest="skills",
        help="특정 스킬만 배포합니다. 여러 번 지정할 수 있습니다.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="배포하지 않고 대상의 버전과 실제 내용 drift를 검사합니다.",
    )
    args = parser.parse_args()

    root = repo_root_from_script(Path(__file__))
    skill_dirs = discover_skills(root)

    if args.skills:
        requested = set(args.skills)
        skill_dirs = [d for d in skill_dirs if d.name in requested]
        missing = requested - {d.name for d in skill_dirs}
        if missing:
            for name in sorted(missing):
                print(f"[error] 알 수 없는 스킬: {name}")
            return 1

    failed = [r for r in (validate_skill(d) for d in skill_dirs) if r.errors]
    if failed:
        for report in failed:
            print(f"[fail] {report.name}: 검증 오류 {len(report.errors)}건 — 배포 중단")
        print("python3 scripts/validate_skills.py 로 먼저 오류를 해결하세요.")
        return 1

    if args.check:
        has_drift = False
        for skill_dir in skill_dirs:
            name = skill_dir.name
            version = skill_version(skill_dir)
            deployed = args.target / name
            current_version = deployed_version(deployed)
            content_state = "일치" if contents_match(skill_dir, deployed) else "drift"
            mark = "=" if current_version == version else "→"
            print(
                f"[check] {name}: 배포본 {current_version} {mark} 레포 {version}; "
                f"내용 {content_state}"
            )
            has_drift = has_drift or current_version != version or content_state == "drift"
        return 1 if has_drift else 0

    previous_versions = {
        skill_dir.name: deployed_version(args.target / skill_dir.name)
        for skill_dir in skill_dirs
    }
    staging_root: Path | None = None
    try:
        staging_root, plans = prepare_deployments(skill_dirs, args.target)
        apply_deployments(plans)
    except DeploymentError as error:
        if staging_root is not None and not error.preserve_staging:
            shutil.rmtree(staging_root, ignore_errors=True)
        print(f"[fail] 배포 중단: {error}", file=sys.stderr)
        if staging_root is not None and error.preserve_staging:
            print(f"[recover] 기존 배포본 백업 보존: {staging_root}", file=sys.stderr)
        return 1

    shutil.rmtree(staging_root, ignore_errors=True)
    for skill_dir in skill_dirs:
        print(
            f"[deploy] {skill_dir.name}: "
            f"{previous_versions[skill_dir.name]} → {skill_version(skill_dir)}"
        )

    print(f"\n배포 완료: {args.target}")
    print("레포에서 삭제된 스킬은 자동으로 지우지 않습니다. 배포 디렉터리를 직접 확인하세요.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
