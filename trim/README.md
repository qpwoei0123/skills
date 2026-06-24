# trim

`version: 0.3.2`

이미 구현된 diff의 동작을 유지하면서 코드량, 중복, 불필요한 복잡도를 줄이는 스킬입니다.

## Quick Start

```text
/trim
/trim --go
/trim -go
```

- `/trim`: 단순화 후보와 검증 계획을 제안한 뒤 승인을 기다립니다.
- `/trim --go`, `/trim -go`: 승인 없이 낮은 위험도의 단순화만 적용합니다.

## Structure

```text
trim/
├── SKILL.md
├── README.md
└── CHANGELOG.md
```

## Test

```bash
# 레포 루트에서 실행
python3 scripts/validate_skills.py --skill trim
```
