# .⚡review

`version: 3.0.0`

닷 스킬(Dot Skills)의 데일리 리뷰입니다. 작은 로컬 diff나 PR/MR을 읽고, 사람이 결정해야 할 제품·데이터·운영 질문을 근거와 함께 추립니다.

## Quick Start

```text
$.⚡review 지금 diff에서 사람이 결정해야 할 질문만 추려줘.
$.⚡review https://github.com/acme/payments/pull/123
$.⚡review 이 MR과 연결된 기획서를 보고 변경의 의도와 영향을 검토해줘.
```

코드·설정·기존 답변에서 알 수 있는 내용은 먼저 확인합니다. 예를 들어 기본값 변경이 기존 고객에게도 적용되는데 연결된 기획에는 신규 고객만 언급되어 있다면, 기존 고객의 전환 정책과 그에 따른 구현 범위를 질문합니다.

질문이 없으면 없다고 끝냅니다. 판단에 꼭 필요한 자료를 읽지 못한 경우에는 제한된 범위를 밝힙니다. 버그·회귀 중심의 코드 리뷰는 별도 작업이며, 이 리뷰 중 확인한 결함도 질문으로 돌리지 않고 그대로 알립니다. 기본 동작은 읽기 전용입니다.

호출명과 목록 표시명은 `.⚡review`, 저장 폴더는 `review`입니다. 기존 `won-context-review` 설치본은 새 스킬을 배포한 뒤 스킬 탐색 경로 밖에 백업해 중복 노출을 막습니다.

## Structure

```text
review/
├── SKILL.md, README.md, CHANGELOG.md
├── agents/openai.yaml
└── references/
    ├── question-rubric.md      # 질문과 코드로 확인할 의문의 구분 예시
    └── source-collection.md    # 원격 PR/MR의 revision·누락 확인
```

## Test

저장소 루트에서 형식을 검사합니다.

```bash
python3 scripts/validate_skills.py --skill .⚡review
python3 scripts/deploy_skills.py --skill .⚡review --check
```
