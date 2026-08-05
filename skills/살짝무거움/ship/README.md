# ship

`version: 0.1.0`

현재 작업을 다듬고 검증해 커밋한 뒤 Draft PR/MR까지 한 번에 만드는 제출 오케스트레이션 스킬입니다. Codex 표시 이름은 **출항**입니다.

## Quick Start

```text
$ship
$ship --go
$ship -go
```

- `$ship`: `trim → annotate → commit → Draft PR/MR` 계획과 최종 제목·본문을 보여줍니다.
- `$ship --go`, `$ship -go`: 계획한 흐름을 push와 Draft 생성까지 끝냅니다.

`--go` 호출 한 번이 현재 리뷰 범위를 다듬고 커밋·push·Draft 생성하는 승인입니다. branch rename, force push, 일반 PR/MR fallback은 하지 않습니다.

worktree가 깨끗해도 base보다 앞선 커밋이 있으면 전체 리뷰 범위를 다듬고, 새 diff가 생긴 경우에만 후속 커밋을 만듭니다. 제출할 변경이 전혀 없으면 빈 커밋 없이 종료합니다.

## Structure

```text
ship/
├── SKILL.md
├── README.md
├── CHANGELOG.md
└── agents/
    └── openai.yaml
```

- `SKILL.md`: 범위 결정, 하위 스킬 순서, 승인 경계, 중단과 보고 계약
- `agents/openai.yaml`: Codex 표시 이름 **출항**과 기본 프롬프트

## Test

```bash
python3 scripts/validate_skills.py --skill ship
```
