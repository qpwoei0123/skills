# context-review

`version: 1.0.0`

PR/MR과 연결 자료에서 사람이 답해야 할 제품·데이터·운영 결정을 근거와 함께 추리는 읽기 전용 스킬입니다.

## Quick Start

```text
$context-review https://github.com/acme/payments/pull/123
$context-review 이 MR과 연결된 기획서를 읽고 사람이 결정해야 할 질문만 추려줘.
```

현재 맥락의 변경과 자료를 재사용하고, 코드·댓글에서 이미 답한 의문은 제거합니다. 질문 수나 고정 보고 틀을 채우지 않으며, 답에 따라 실제 결정이 달라지는 질문만 남깁니다. 핵심 자료에 접근하지 못한 경우와 유효한 질문이 없는 경우를 구분합니다.

PR/MR·파일·댓글은 변경하지 않습니다. 일반 버그·회귀 검토는 `review` 또는 `code-review`의 범위입니다.

## Structure

```text
context-review/
├── SKILL.md, README.md, CHANGELOG.md
├── agents/openai.yaml
└── references/
    ├── question-rubric.md      # 질문의 근거·결정·신규성
    └── source-collection.md    # revision·discussion·누락 확인
```

## Test

저장소 루트에서 형식을 검사합니다.

```bash
python3 scripts/validate_skills.py --skill context-review
```
