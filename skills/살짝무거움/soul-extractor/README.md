# soul-extractor

`version: 0.3.1`

허가된 사람, 브랜드, 캐릭터의 글 샘플에서 문체 지문을 만들고 스타일 일치도를 점검해 글을 다듬는 스킬입니다.

## Quick Start

```text
soul-extractor
soul-extractor "이 글을 내 스타일로 다듬어줘"
소울 익스트랙터
```

- 프로필이 없으면 샘플 수집과 문체 지문 생성부터 시작합니다.
- 프로필이 있으면 변환, 작성, 채점 중 필요한 작업을 진행합니다.
- 결과에는 스타일 일치도와 부족한 점을 함께 보고합니다.

## Structure

```text
soul-extractor/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── agents/
│   └── openai.yaml
├── scripts/
│   ├── setup.sh
│   ├── score.py
│   └── test_score.py
├── references/
│   └── profile-template.md
└── evals/
    └── trigger-eval.json
```

런타임 데이터는 스킬 폴더가 아니라 `~/.soul-extractor/` 아래에 저장합니다.

## Scripts

아래 명령은 `soul-extractor` 스킬 폴더에서 실행합니다.

- `scripts/setup.sh`: 런타임 데이터 디렉터리(`~/.soul-extractor/profiles`)를 보장합니다.

  ```bash
  bash scripts/setup.sh
  ```

- `scripts/score.py`: 점수표 항목 점수를 받아 총점과 등급을 재현 가능하게 계산합니다. 항목 순서·개수·각 배점은 SKILL.md 점수표와 같습니다.

  ```bash
  python3 scripts/score.py completeness 16 14 24 8 15
  python3 scripts/score.py match 17 16 18 17 8 8
  ```

## Test

```bash
# 레포 루트에서 실행
python3 scripts/validate_skills.py --skill soul-extractor

# 레포 루트에서 실행
python3 -m unittest discover -s skills/살짝무거움/soul-extractor/scripts -p 'test_*.py'
```
