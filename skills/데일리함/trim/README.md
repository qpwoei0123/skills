# trim

`version: 0.4.0`

이미 구현된 diff의 동작을 유지하면서 군더더기를 덜어내고, 흩어진 중복·패턴을 같은 이유로 변하는 단위로 엮는 스킬입니다. (weave 스킬을 흡수 통합)

## Quick Start

```text
/trim
/trim --go
/trim -go
```

- `/trim`: 덜어내기·엮기 후보와 검증 계획을 제안한 뒤 승인을 기다립니다.
- `/trim --go`, `/trim -go`: 승인 없이 근거 1·2등급 후보만 적용합니다.

## Structure

```text
trim/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── references/
│   └── weave-criteria.md
└── evals/
    └── trigger-eval.json
```

## Test

```bash
# 레포 루트에서 실행
python3 scripts/validate_skills.py --skill trim
```
