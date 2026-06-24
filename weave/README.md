# weave

`version: 0.2.0`

흩어진 코드와 패턴을 같은 이유로 변하는 단위로 엮어 일관된 구조로 정리하는 스킬입니다.

## Quick Start

```text
/weave
/weave --go
/weave -go
```

- `/weave`: 엮을 후보와 보류할 후보를 제안한 뒤 승인을 기다립니다.
- `/weave --go`, `/weave -go`: 승인 없이 낮은 위험도의 weave만 적용합니다.

## Structure

```text
weave/
├── SKILL.md
├── README.md
└── CHANGELOG.md
```

## Test

```bash
# 레포 루트에서 실행
python3 scripts/validate_skills.py --skill weave
```
