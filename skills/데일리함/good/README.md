# .⚡good

`version: 2.0.0`

코드의 동작을 유지하면서 복잡성과 중복을 줄이고, 코드만으로 드러나지 않는 맥락을 주석으로 남깁니다. 기존 `trim`과 `annotate`를 통합했습니다.

## Quick Start

```text
$.⚡good 이번 변경을 읽고 수정하기 쉽게 다듬어줘.
$.⚡good 이 분기가 필요한 이유만 주석으로 남겨줘. 코드는 그대로 둬.
$.⚡good 주석 추가 없이 중복만 줄여줘.
$.⚡good 수정하지 말고 후보만 보여줘.
```

기본 호출은 실행합니다. `/.⚡good`, `--go`, `-go`도 받을 수 있으며, "계획만"이라는 제한은 실행 표기보다 우선합니다. 설계 모델을 다시 판단할 때는 `.⚡wow`를 사용합니다.

`$trim`과 `$annotate`는 명시 호출 별칭으로 제공하지 않습니다. 기존 호출을 `$.⚡good` 또는 `$.⚡good 주석만`으로 바꿉니다.

## Structure

```text
good/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── agents/openai.yaml
├── references/weave-criteria.md
└── evals/trigger-eval.json
```

## Test

```bash
python3 scripts/validate_skills.py --skill .⚡good
```
