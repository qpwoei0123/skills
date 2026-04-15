#!/usr/bin/env python3
"""Select autofixable skill normalization targets for GitHub Actions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def slugify(value: str) -> str:
    import re

    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "branch"


def changed_skill_names(changed_files: list[str], repo_root: Path) -> list[str]:
    skills: set[str] = set()
    for file_path in changed_files:
        parts = Path(file_path).parts
        if not parts:
            continue
        candidate = repo_root / parts[0]
        if candidate.is_dir() and (candidate / "SKILL.md").exists():
            skills.add(parts[0])
    return sorted(skills)


def build_targets(
    validate_payload: dict[str, object],
    changed_files: list[str],
    base_branch: str,
    trigger_sha: str,
    repo_root: Path,
) -> dict[str, object]:
    reports = validate_payload.get("skills", [])
    if not isinstance(reports, list):
        return {"include": []}

    candidate_names = set(changed_skill_names(changed_files, repo_root))
    targets = []

    for report in reports:
        if not isinstance(report, dict):
            continue
        name = report.get("name")
        errors = report.get("errors", [])
        if not isinstance(name, str) or name not in candidate_names or not isinstance(errors, list):
            continue
        if not errors:
            continue

        autofixable = True
        for error in errors:
            if not isinstance(error, dict) or not error.get("autofixable"):
                autofixable = False
                break
        if not autofixable:
            continue

        targets.append(
            {
                "skill": name,
                "branch": f"codex/normalize-{slugify(name)}",
                "title": f"Normalize {name} to repository skill standard",
                "body": "\n".join(
                    [
                        "## Why",
                        "",
                        f"`{base_branch}` push({trigger_sha[:7]})에서 저장소 표준을 통과하지 못한 스킬의 구조적 항목만 자동 보정합니다.",
                        "",
                        "## Automatic scope",
                        "",
                        "- frontmatter 구조 정리",
                        "- README 골격/버전/필수 섹션 보강",
                        "- CHANGELOG 최신 버전 헤더 보강",
                        "",
                        "의미를 바꾸는 수정은 포함하지 않습니다.",
                    ]
                ),
            }
        )

    return {"include": targets}


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute normalize PR targets.")
    parser.add_argument("--validate-json", required=True, help="validator JSON 경로")
    parser.add_argument(
        "--changed-files-json",
        required=True,
        help="GitHub PR changed files JSON 배열",
    )
    parser.add_argument("--base-branch", required=True, help="normalize PR의 base 브랜치")
    parser.add_argument("--trigger-sha", required=True, help="자동 정규화를 유발한 커밋 SHA")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    validate_payload = json.loads(Path(args.validate_json).read_text(encoding="utf-8"))
    changed_files = json.loads(args.changed_files_json)
    payload = build_targets(
        validate_payload,
        changed_files,
        args.base_branch,
        args.trigger_sha,
        repo_root,
    )
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
