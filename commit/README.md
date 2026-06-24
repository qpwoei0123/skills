# commit

`version: 0.3.2`

현재 git 변경사항을 읽고 최근 커밋 로그 스타일에 맞춰 Conventional Commits 형식의 한글 커밋을 계획하거나 실행하는 스킬입니다.

## Quick Start

```text
/commit
/commit --go
/commit -go
```

- `/commit`: diff를 분석하고 커밋 계획을 제안한 뒤 승인을 기다립니다.
- `/commit --go`, `/commit -go`: 승인 없이 바로 적절한 단위로 커밋합니다.

## Structure

```text
commit/
├── SKILL.md
├── README.md
└── CHANGELOG.md
```

## Test

```bash
python3 scripts/validate_skills.py --skill commit
```
