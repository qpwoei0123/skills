#!/usr/bin/env python3
"""Validate accepted skills against the repository skill standard."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from skill_repo_lib import (
    build_json_payload,
    discover_skills,
    dumps_json,
    repo_root_from_script,
    validate_skill,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate skills in this repository.")
    parser.add_argument(
        "--skill",
        action="append",
        dest="skills",
        help="특정 스킬 이름만 검사합니다. 여러 번 지정할 수 있습니다.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="기계 판정용 JSON 결과를 출력합니다.",
    )
    args = parser.parse_args()

    root = repo_root_from_script(Path(__file__))
    skill_dirs = discover_skills(root)

    if args.skills:
        requested = set(args.skills)
        skill_dirs = [skill for skill in skill_dirs if skill.name in requested]
        missing = requested - {skill.name for skill in skill_dirs}
        if missing:
            if args.json:
                payload = {
                    "skills": [],
                    "summary": {"skills": 0, "errors": len(missing), "warnings": 0},
                    "missing_skills": sorted(missing),
                }
                print(dumps_json(payload))
            else:
                for name in sorted(missing):
                    print(f"[error] 알 수 없는 스킬: {name}")
            return 1

    reports = [validate_skill(skill_dir) for skill_dir in skill_dirs]
    payload = build_json_payload(reports)

    if args.json:
        print(dumps_json(payload))
        return 1 if payload["summary"]["errors"] else 0

    error_count = 0
    warning_count = 0
    for report in reports:
        if not report.errors and not report.warnings:
            print(f"[ok] {report.name}")
            continue

        if report.errors:
            print(f"[fail] {report.name}")
            for error in report.errors:
                print(f"  - error: [{error.code}] {error.message}")
            error_count += len(report.errors)
        else:
            print(f"[ok] {report.name}")

        for warning in report.warnings:
            print(f"  - warn: [{warning.code}] {warning.message}")
            warning_count += 1

    print(f"\nSummary: skills={len(reports)} errors={error_count} warnings={warning_count}")
    return 1 if error_count else 0


if __name__ == "__main__":
    sys.exit(main())
