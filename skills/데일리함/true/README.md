# .⚡true

`version: 0.1.0`

지금 하는 일이 진짜 원하는 결과로 이어지는지 짚어 줍니다. 요청한 방법 뒤에 다른 목적이 보이면 근거와 함께 짧게 제안합니다.

## Quick Start

```text
$.⚡true 지금 만드는 셀렉트 리스트가 내가 원하는 사용 방식에 맞는지 봐줘.
$.⚡true 이 작업의 방향이 맞는지, 혹시 더 직접적인 방법이 있는지 짚어줘.
```

목적을 단정하지 않고, 현재 요청과 작업물에서 확인되는 행동을 근거로 가설을 제시합니다. 방향 점검만 요청했다면 제안까지 합니다.

## Structure

```text
true/
├── SKILL.md
├── README.md
├── CHANGELOG.md
└── agents/openai.yaml
```

## Test

```bash
python3 scripts/validate_skills.py --skill .⚡true
python3 scripts/sync_skill_rules.py --check
```
