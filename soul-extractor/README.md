# soul-extractor

`version: 0.2.0`

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
├── references/
│   └── profile-template.md
└── evals/
    └── trigger-eval.json
```

런타임 데이터는 스킬 폴더가 아니라 `~/.soul-extractor/` 아래에 저장합니다.

## Test

```bash
# 레포 루트에서 실행
python3 scripts/validate_skills.py --skill soul-extractor
```
