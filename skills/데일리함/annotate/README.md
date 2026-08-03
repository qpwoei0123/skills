# annotate

`version: 0.2.2`

현재 작업과 관련된 로직을 읽기 쉽게 짧은 한글 주석으로 정리하는 스킬입니다.

## Quick Start

```text
/annotate
/annotate --go
/annotate -go
```

- `/annotate`: 주석 후보를 제안한 뒤 승인을 기다립니다.
- `/annotate --go`, `/annotate -go`: 승인 없이 명확히 필요한 낮은 위험도의 주석만 반영합니다.

## Structure

```text
annotate/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── agents/
│   └── openai.yaml
└── evals/
    └── trigger-eval.json
```

## Test

```bash
# 레포 루트에서 실행
python3 scripts/validate_skills.py --skill annotate
```
