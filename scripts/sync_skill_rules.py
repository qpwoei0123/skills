#!/usr/bin/env python3
"""선택한 규칙 모듈을 SKILL.md에 조립한다. 기본 동작은 읽기 전용 정합성 검사다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from skill_repo_lib import discover_skills, repo_root_from_script

START = "<!-- common-rules:start -->"
END = "<!-- common-rules:end -->"
GROUPS = ("readability", "predictability", "cohesion", "coupling")


def render_skill(text: str, block: str) -> str:
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("frontmatter 경계를 확인할 수 없습니다")
    boundary = text.index("\n---\n", 4) + len("\n---\n")
    header, body = text[:boundary], text[boundary:]
    if START in text or END in text:
        if text.count(START) != 1 or text.count(END) != 1:
            raise ValueError("공통 규칙 표식이 중복되거나 짝이 없습니다")
        start, end = body.find(START), body.find(END)
        if start < 0 or end < start:
            raise ValueError("공통 규칙 표식의 위치나 순서가 잘못되었습니다")
        body = body[:start] + body[end + len(END):]
    return header + "\n" + (block + "\n\n" if block else "") + body.lstrip("\n")


def planned_changes(root: Path) -> list[tuple[Path, str]]:
    rules = root / "rules"
    assignments = json.loads((rules / "skills.json").read_text(encoding="utf-8"))
    skills = discover_skills(root)
    names = [path.name for path in skills]
    if len(names) != len(set(names)):
        raise ValueError("스킬 폴더명이 중복됩니다")
    if not isinstance(assignments, dict) or set(assignments) != set(names):
        raise ValueError("rules/skills.json에 현재 스킬을 빠짐없이 배정해야 합니다 (미적용은 빈 modules)")
    modules = {
        path.stem: path.read_text(encoding="utf-8").strip()
        for path in sorted((rules / "modules").glob("*.md"))
    }
    for name, content in modules.items():
        if name.split("-", 1)[0] not in GROUPS or not content or START in content or END in content:
            raise ValueError(f"잘못된 규칙 모듈: {name}")
    order = sorted(modules, key=lambda name: (GROUPS.index(name.split("-", 1)[0]), name))
    if not order:
        raise ValueError("규칙 모듈이 없습니다")
    changes = []
    for skill in skills:
        assignment = assignments[skill.name]
        if not isinstance(assignment, dict) or set(assignment) - {"modules", "application"}:
            raise ValueError(f"잘못된 배정 형식: {skill.name}")
        selected = assignment.get("modules")
        if not isinstance(selected, list) or any(not isinstance(name, str) for name in selected):
            raise ValueError(f"modules는 문자열 목록이어야 합니다: {skill.name}")
        if selected == ["*"]:
            selected = order
        if len(selected) != len(set(selected)) or set(selected) - set(modules):
            raise ValueError(f"알 수 없거나 중복된 모듈: {skill.name}")
        application = assignment.get("application", "")
        if not isinstance(application, str) or (selected and not application.strip()):
            raise ValueError(f"규칙 적용 범위가 필요합니다: {skill.name}")
        if START in application or END in application:
            raise ValueError(f"규칙 적용 범위에 생성 표식을 넣을 수 없습니다: {skill.name}")
        block = ""
        if selected:
            sections = [modules[name] for name in order if name in selected]
            block = "\n\n".join([
                START,
                "## 공통 판단 기준",
                "현재 요청과 이 스킬의 작업 범위 안에서 관련 있는 기준만 적용한다. "
                "규칙을 충족하려고 요청 밖 수정이나 형식적인 보고 항목을 추가하지 않는다.",
                application.strip(),
                *sections,
                "출처: [Toss Frontend Fundamentals](https://frontend-fundamentals.com/code-quality/code/)의 "
                "코드 품질 기준을 작업별로 재구성했다.",
                END,
            ])
        path = skill / "SKILL.md"
        before = path.read_text(encoding="utf-8")
        after = render_skill(before, block)
        if before != after:
            changes.append((path, after))
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="차이가 있는 스킬 본문 갱신")
    mode.add_argument("--check", action="store_true", help="미동기화 시 실패 (기본)")
    args = parser.parse_args()
    root = repo_root_from_script(Path(__file__))
    try:
        changes = planned_changes(root)
    except (OSError, ValueError) as error:
        print(f"[error] {error}")
        return 1
    # 모든 입력과 표식을 확인한 뒤에만 쓰기 시작한다.
    for path, content in changes:
        if args.write:
            path.write_text(content, encoding="utf-8")
        print(f"[{'updated' if args.write else 'stale'}] {path.relative_to(root)}")
    if changes and not args.write:
        print("python3 scripts/sync_skill_rules.py --write 로 동기화하세요.")
        return 1
    print(f"[ok] 공통 규칙 {'갱신' if args.write else '일치'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
