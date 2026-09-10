# soul-extractor

`version: 1.0.0`

본인·허가된 사람·브랜드·캐릭터의 글에서 문체 지문을 추출해 글을 작성하거나 다듬습니다.

## Quick Start

```text
$soul-extractor 이 글을 내 샘플의 말투로 다듬어줘.
$soul-extractor 이 샘플에서 문체 프로필을 만들어 저장해줘.
$soul-extractor 이 초안의 문체 일치도를 채점해줘.
```

필요한 작업만 실행합니다. 샘플 개수로 작성을 막지 않고 근거가 허용하는 범위의 초안을 만듭니다. 본인이나 허가된 대상임을 이미 알면 다시 묻지 않습니다. 문체 때문에 없는 경험·입장·약속을 추가하지 않습니다.

점수는 요청할 때만 제공합니다. 일회성 변환에 프로필 저장을 강제하지 않으며, 저장 요청은 `~/.soul-extractor/profiles/<profile-id>.md`에 반영합니다. 사용자 피드백과 원본 샘플을 구분하고 생성한 글을 저자의 새 샘플로 사용하지 않습니다.

## Structure

```text
soul-extractor/
├── SKILL.md, README.md, CHANGELOG.md
├── agents/openai.yaml
├── references/profile-template.md
├── evals/trigger-eval.json
└── scripts/
    ├── setup.sh
    ├── score.py
    └── test_score.py
```

## Scripts

스킬 폴더에서 실행합니다. `setup.sh`는 저장 요청이 있을 때 런타임 디렉터리를 준비합니다. `score.py`는 평가자가 근거를 붙여 정한 항목 점수의 합과 참고 등급을 계산합니다. 문체를 자동 측정하거나 저자를 판별하는 도구는 아닙니다. 항목 순서와 배점은 [프로필 템플릿](references/profile-template.md)을 따릅니다.

```bash
bash scripts/setup.sh
python3 scripts/score.py completeness 16 14 24 8 15
python3 scripts/score.py match 17 16 18 17 8 8
```

기존 등급의 숫자 경계는 초안 작성 허용 기준으로 쓰지 않습니다.

## Test

저장소 루트에서 기존 검증을 실행합니다.

```bash
python3 scripts/validate_skills.py --skill soul-extractor
python3 -m unittest discover -s skills/살짝무거움/soul-extractor/scripts -p 'test_*.py'
```
