# .⚡wow

`version: 2.1.0`

문제 정의와 설계 모델을 다시 보고, 더 적은 상태와 책임으로 같은 목표를 이루는 방식을 제안합니다.

## Quick Start

```text
$.⚡wow 이 상태 관리를 처음부터 다시 본다면 어떤 개념을 없앨 수 있어?
$.⚡wow 재설계안을 먼저 보여줘. 선택하면 구현하자.
$.⚡wow 가장 나은 안을 골라 구현까지 해줘.
```

기본 호출과 `/.⚡wow`는 제안까지 수행합니다. 사용자가 선택과 구현도 맡겼다면 같은 요청 안에서 구현을 이어갑니다. 현재 동작을 유지하며 코드를 정리할 때는 `.⚡good`을 사용합니다.

## Structure

```text
wow/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── agents/openai.yaml
├── references/example.md
└── evals/trigger-eval.json
```

## Test

```bash
python3 scripts/validate_skills.py --skill .⚡wow
```
