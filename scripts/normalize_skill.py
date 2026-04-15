#!/usr/bin/env python3
"""Normalize skill metadata and docs to the repository standard."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from skill_repo_lib import (
    NormalizeResult,
    build_json_payload,
    load_frontmatter_document,
    metadata_version,
    normalize_changelog_content,
    normalize_readme_content,
    parse_frontmatter,
    render_frontmatter_document,
    repo_root_from_script,
    upsert_metadata_version,
    validate_skill,
)


def load_template(repo_root: Path, name: str, **kwargs: str) -> str:
    template_path = repo_root / "templates" / "skill" / name
    return template_path.read_text(encoding="utf-8").format(**kwargs).rstrip() + "\n"


def manual_blockers(skill_dir: Path):
    report = validate_skill(skill_dir)
    return [error for error in report.errors if not error.autofixable]


def normalize_skill_directory(skill_dir: Path, repo_root: Path, write: bool) -> NormalizeResult:
    result = NormalizeResult(skill=skill_dir.name)
    blockers = manual_blockers(skill_dir)
    if blockers:
        result.blockers.extend(blockers)
        return result

    skill_path = skill_dir / "SKILL.md"
    skill_text = skill_path.read_text(encoding="utf-8")
    document = load_frontmatter_document(skill_text)
    frontmatter = parse_frontmatter(skill_text)
    changed_frontmatter, resolved_version = upsert_metadata_version(document)
    if not resolved_version:
        resolved_version = metadata_version(frontmatter)

    pending_writes: list[tuple[Path, str]] = []
    if changed_frontmatter:
        pending_writes.append((skill_path, render_frontmatter_document(document)))
        result.applied_changes.append("SKILL.md metadata.version 정규화")

    readme_path = skill_dir / "README.md"
    if readme_path.exists():
        readme_text = readme_path.read_text(encoding="utf-8")
        normalized_readme, readme_changes = normalize_readme_content(
            skill_name=skill_dir.name,
            version=resolved_version,
            text=readme_text,
        )
        if normalized_readme != readme_text:
            pending_writes.append((readme_path, normalized_readme))
            result.applied_changes.extend(readme_changes)
    else:
        pending_writes.append(
            (
                readme_path,
                load_template(
                    repo_root,
                    "README.md.tmpl",
                    skill_name=skill_dir.name,
                    version=resolved_version,
                ),
            )
        )
        result.applied_changes.append("README.md 생성")

    changelog_path = skill_dir / "CHANGELOG.md"
    if changelog_path.exists():
        changelog_text = changelog_path.read_text(encoding="utf-8")
        normalized_changelog, changelog_changes = normalize_changelog_content(
            version=resolved_version,
            text=changelog_text,
        )
        if normalized_changelog != changelog_text:
            pending_writes.append((changelog_path, normalized_changelog))
            result.applied_changes.extend(changelog_changes)
    else:
        pending_writes.append(
            (
                changelog_path,
                load_template(
                    repo_root,
                    "CHANGELOG.md.tmpl",
                    skill_name=skill_dir.name,
                    version=resolved_version,
                ),
            )
        )
        result.applied_changes.append("CHANGELOG.md 생성")

    if write:
        for path, content in pending_writes:
            path.write_text(content, encoding="utf-8")

        validation = validate_skill(skill_dir)
        if validation.errors:
            result.remaining_errors.extend(validation.errors)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize a skill to repository standard.")
    parser.add_argument("--skill", required=True, help="정규화할 스킬 이름")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="실제로 파일을 수정합니다.")
    mode.add_argument("--check", action="store_true", help="변경 필요 여부만 출력합니다.")
    args = parser.parse_args()

    repo_root = repo_root_from_script(Path(__file__))
    skill_dir = repo_root / args.skill
    if not skill_dir.exists() or not (skill_dir / "SKILL.md").exists():
        print(f"[error] 알 수 없는 스킬: {args.skill}")
        return 1

    result = normalize_skill_directory(skill_dir, repo_root=repo_root, write=args.write)
    if result.blockers:
        print(f"[block] {result.skill}")
        for blocker in result.blockers:
            print(f"  - [{blocker.code}] {blocker.message}")
        return 1

    if args.check:
        if result.applied_changes:
            print(f"[needs_changes] {result.skill}")
            for change in result.applied_changes:
                print(f"  - {change}")
            return 1

        print(f"[ok] {result.skill}")
        return 0

    if result.remaining_errors:
        print(f"[fail] {result.skill}")
        for error in result.remaining_errors:
            print(f"  - [{error.code}] {error.message}")
        payload = build_json_payload([validate_skill(skill_dir)])
        print(payload["summary"])
        return 1

    if result.applied_changes:
        print(f"[normalized] {result.skill}")
        for change in result.applied_changes:
            print(f"  - {change}")
    else:
        print(f"[ok] {result.skill}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
