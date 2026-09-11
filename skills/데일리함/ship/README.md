# .⚡ship

`version: 3.1.0`

닷 스킬(Dot Skills)의 PR/MR 준비 도구입니다. `.⚡commit`의 연장선에서 필요한 diff를 커밋하고, 저장소 관례에 맞는 제목·본문을 완성합니다. 기존 `mr`과 `won-ship`을 통합했습니다.

## Quick Start

```text
$.⚡ship
$.⚡ship 이 작업은 커밋하고, 무관한 diff는 남겨둔 채 PR 본문까지 준비해줘.
$.⚡ship 변경분 커밋하고 Draft PR까지 올려줘.
$.⚡ship 기존 Draft에 이번 작업을 이어서 반영해줘.
$.⚡ship 수정하지 말고 커밋 계획과 본문안만 보여줘.
```

기본 호출은 필요한 커밋과 제목·본문안까지입니다. push·생성·갱신을 요청했거나 같은 작업에서 이미 맡겼으면 그 범위까지 이어갑니다. "계획만"이면 읽기 전용, "기존 커밋만"·"본문만"이면 새 커밋을 만들지 않습니다. 원격 본문만 갱신할 때는 원격에 있는 변경으로 설명을 작성합니다.

애매하거나 무관한 diff는 판단해서 남길 수 있습니다. 실제 제출 내용이 남긴 변경에 의존하지 않는지 확인하고, 본문은 제출한 변경만 설명합니다. 코드 정리는 요청한 경우에 `.⚡good`을 함께 사용합니다.

새 요청은 Draft로 만들고, 기존 Draft의 본문은 사용자가 쓴 내용과 `ship:managed` 표식을 보존하며 갱신합니다. 인증된 CLI와 HTTPS 경로를 사용합니다.

## Structure

```text
ship/
├── SKILL.md, README.md, CHANGELOG.md
├── agents/openai.yaml
├── evals/trigger-eval.json
├── references/
│   ├── branch-conventions.md
│   ├── review-format.md
│   └── draft-update.md
└── scripts/preflight.sh
```

## Scripts

대상 git 저장소에서 읽기 전용 개요를 확인합니다.

```bash
bash <스킬 디렉터리>/scripts/preflight.sh
```

## Test

```bash
python3 scripts/validate_skills.py --skill .⚡ship
```
