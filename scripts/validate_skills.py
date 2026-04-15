#!/usr/bin/env python3
"""Validate accepted skills against the repository skill standard."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
README_VERSION_RE = re.compile(r"version:\s*([0-9]+\.[0-9]+\.[0-9]+)", re.IGNORECASE)
CHANGELOG_VERSION_RE = re.compile(r"^##\s+([0-9]+\.[0-9]+\.[0-9]+)\s*$", re.MULTILINE)

QUICKSTART_MARKERS = ("## Quick Start", "## 사용 예시", "## Quickstart")
STRUCTURE_MARKERS = ("## Structure", "## 포함 파일", "## 디렉터리 구조")
TEST_MARKERS = ("## Test", "## 테스트", "## 검증 방법")


@dataclass
class SkillReport:
    name: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def parse_frontmatter(text: str) -> dict[str, object]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("frontmatter opening '---'가 없습니다.")

    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break
    if end_index is None:
        raise ValueError("frontmatter closing '---'가 없습니다.")

    data: dict[str, object] = {}
    current_parent: str | None = None

    for raw in lines[1:end_index]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue

        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()

        if indent == 0:
            if stripped.endswith(":") and ":" not in stripped[:-1]:
                current_parent = stripped[:-1].strip()
                data[current_parent] = {}
                continue

            if ":" not in stripped:
                continue

            key, value = stripped.split(":", 1)
            data[key.strip()] = value.strip()
            current_parent = None
            continue

        if current_parent and ":" in stripped and isinstance(data.get(current_parent), dict):
            key, value = stripped.split(":", 1)
            nested = data[current_parent]
            assert isinstance(nested, dict)
            nested[key.strip()] = value.strip()

    return data


def contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)


def validate_skill(skill_dir: Path) -> SkillReport:
    report = SkillReport(name=skill_dir.name)

    required_files = ("SKILL.md", "README.md", "CHANGELOG.md")
    for filename in required_files:
        if not (skill_dir / filename).exists():
            report.errors.append(f"필수 파일 누락: {filename}")

    skill_path = skill_dir / "SKILL.md"
    if not skill_path.exists():
        return report

    skill_text = skill_path.read_text(encoding="utf-8")
    try:
        frontmatter = parse_frontmatter(skill_text)
    except ValueError as exc:
        report.errors.append(f"SKILL.md frontmatter 오류: {exc}")
        return report

    for key in ("name", "license", "description"):
        value = frontmatter.get(key)
        if not isinstance(value, str) or not value:
            report.errors.append(f"frontmatter 필수 키 누락 또는 빈 값: {key}")

    metadata = frontmatter.get("metadata")
    version = ""
    if not isinstance(metadata, dict):
        report.errors.append("frontmatter 필수 키 누락: metadata.version")
    else:
        meta_version = metadata.get("version")
        if not isinstance(meta_version, str) or not meta_version:
            report.errors.append("frontmatter 필수 키 누락 또는 빈 값: metadata.version")
        else:
            version = meta_version
            if not SEMVER_RE.match(version):
                report.errors.append(f"metadata.version이 SemVer 형식이 아님: {version}")

    readme_path = skill_dir / "README.md"
    if readme_path.exists():
        readme_text = readme_path.read_text(encoding="utf-8")
        version_match = README_VERSION_RE.search(readme_text)
        if not version_match:
            report.errors.append("README.md에 version 표기가 없습니다.")
        elif version and version_match.group(1) != version:
            report.errors.append(
                f"README.md version 불일치: {version_match.group(1)} != {version}"
            )

        if not contains_any(readme_text, QUICKSTART_MARKERS):
            report.errors.append("README.md에 Quick Start/사용 예시 섹션이 없습니다.")
        if not contains_any(readme_text, STRUCTURE_MARKERS):
            report.errors.append("README.md에 Structure/포함 파일/디렉터리 구조 섹션이 없습니다.")
        if not contains_any(readme_text, TEST_MARKERS):
            report.errors.append("README.md에 Test/테스트/검증 방법 섹션이 없습니다.")

    changelog_path = skill_dir / "CHANGELOG.md"
    if changelog_path.exists():
        changelog_text = changelog_path.read_text(encoding="utf-8")
        match = CHANGELOG_VERSION_RE.search(changelog_text)
        if not match:
            report.errors.append("CHANGELOG.md에 버전 헤더(## x.y.z)가 없습니다.")
        elif version and match.group(1) != version:
            report.errors.append(
                f"CHANGELOG.md 최신 버전 불일치: {match.group(1)} != {version}"
            )

    for dirname in ("agents", "references", "scripts", "assets"):
        dir_path = skill_dir / dirname
        if dir_path.exists() and dir_path.is_dir():
            has_files = any(child.is_file() for child in dir_path.rglob("*"))
            if not has_files:
                report.warnings.append(f"빈 선택 디렉터리: {dirname}/")

    return report


def discover_skills(root: Path) -> list[Path]:
    return sorted(
        child
        for child in root.iterdir()
        if child.is_dir() and not child.name.startswith(".") and (child / "SKILL.md").exists()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate skills in this repository.")
    parser.add_argument(
        "--skill",
        action="append",
        dest="skills",
        help="특정 스킬 이름만 검사합니다. 여러 번 지정할 수 있습니다.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    skill_dirs = discover_skills(root)

    if args.skills:
        requested = set(args.skills)
        skill_dirs = [skill for skill in skill_dirs if skill.name in requested]
        missing = requested - {skill.name for skill in skill_dirs}
        for name in sorted(missing):
            print(f"[error] 알 수 없는 스킬: {name}")
        if missing:
            return 1

    reports = [validate_skill(skill_dir) for skill_dir in skill_dirs]

    error_count = 0
    warning_count = 0
    for report in reports:
        if not report.errors and not report.warnings:
            print(f"[ok] {report.name}")
            continue

        if report.errors:
            print(f"[fail] {report.name}")
            for error in report.errors:
                print(f"  - error: {error}")
            error_count += len(report.errors)
        else:
            print(f"[ok] {report.name}")

        for warning in report.warnings:
            print(f"  - warn: {warning}")
            warning_count += 1

    print(
        f"\nSummary: skills={len(reports)} errors={error_count} warnings={warning_count}"
    )
    return 1 if error_count else 0


if __name__ == "__main__":
    sys.exit(main())
