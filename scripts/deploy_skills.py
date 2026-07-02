#!/usr/bin/env python3
"""Validate 통과한 정식 스킬을 로컬 배포 디렉터리(~/.agents/skills)로 동기화한다."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from skill_repo_lib import (
    discover_skills,
    metadata_version,
    parse_frontmatter,
    repo_root_from_script,
    validate_skill,
)


def skill_version(skill_dir: Path) -> str:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    return metadata_version(parse_frontmatter(text))


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
        help="배포하지 않고 대상과 버전 차이만 출력합니다.",
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

    for skill_dir in skill_dirs:
        name = skill_dir.name
        version = skill_version(skill_dir)
        deployed = args.target / name
        deployed_version = (
            skill_version(deployed) if (deployed / "SKILL.md").exists() else "없음"
        )

        if args.check:
            mark = "=" if deployed_version == version else "→"
            print(f"[check] {name}: 배포본 {deployed_version} {mark} 레포 {version}")
            continue

        if deployed.exists():
            shutil.rmtree(deployed)
        shutil.copytree(skill_dir, deployed)
        print(f"[deploy] {name}: {deployed_version} → {version}")

    if not args.check:
        print(f"\n배포 완료: {args.target}")
        print("레포에서 삭제된 스킬은 자동으로 지우지 않습니다. 배포 디렉터리를 직접 확인하세요.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
