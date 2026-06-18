# mr

`version: 0.3.1`

현재 브랜치의 커밋과 diff를 읽고 GitHub PR 또는 GitLab MR을 항상 draft로 계획하거나 생성하는 스킬입니다.

## Quick Start

```text
/mr
/mr --go
/mr -go
```

- `/mr`: draft MR/PR 계획을 제안한 뒤 승인을 기다립니다.
- `/mr --go`, `/mr -go`: 승인 없이 push 후 draft MR/PR을 생성합니다.

## Structure

```text
mr/
├── SKILL.md
├── README.md
└── CHANGELOG.md
```

## Test

```bash
python3 scripts/validate_skills.py --skill mr
```
