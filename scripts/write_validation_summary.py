#!/usr/bin/env python3
"""Write a GitHub Actions step summary for skill validation."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Write validation summary markdown.")
    parser.add_argument("--validate-json", required=True, help="validator JSON 경로")
    parser.add_argument(
        "--changed-files-json",
        required=True,
        help="PR changed files JSON 배열",
    )
    args = parser.parse_args()

    changed_files = json.loads(args.changed_files_json)
    validate_payload = json.loads(Path(args.validate_json).read_text(encoding="utf-8"))
    changed_skills = sorted({path.split("/", 1)[0] for path in changed_files if "/" in path})

    lines = ["## Skill Validation Summary", ""]
    if changed_skills:
        lines.append(f"- Changed top-level paths: {', '.join(changed_skills)}")
    else:
        lines.append("- Changed top-level paths: none")

    skill_reports = {skill["name"]: skill for skill in validate_payload.get("skills", [])}
    for skill_name in changed_skills:
        report = skill_reports.get(skill_name)
        if not report or not report.get("errors"):
            continue

        manual_errors = [error for error in report["errors"] if not error.get("autofixable")]
        if not manual_errors:
            continue

        lines.append("")
        lines.append(f"### {skill_name}")
        for error in manual_errors:
            lines.append(f"- manual: [{error['code']}] {error['message']}")

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        Path(summary_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        print("\n".join(lines))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
