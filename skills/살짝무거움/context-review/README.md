# context-review

`version: 0.1.0`

큰 PR/MR과 관련 자료를 행동 단위로 구조화하고, 코드가 아니라 사람이 답해야 할 고맥락 리뷰 질문만 근거와 함께 추리는 읽기 전용 스킬입니다.

## Quick Start

```text
$context-review https://github.com/acme/payments/pull/123
```

```text
$context-review로 이 MR과 기획서·마이그레이션 계획을 함께 읽고 사람이 답할 질문만 추려 주세요.
MR: https://gitlab.com/acme/payments/-/merge_requests/123
기획서: https://...
마이그레이션: https://...
```

스킬은 변경을 행동 단위로 묶고 연결 자료에서 이미 답한 내용을 제거한 뒤, 답에 따라 병합·배포 결정이 달라지는 질문만 최대 7개 제시합니다. 유효한 질문이 없으면 0개로 끝냅니다.

일반적인 버그·회귀 finding은 `review` 또는 `code-review`의 역할입니다. 이 스킬은 파일, PR/MR 상태, 댓글을 변경하지 않습니다.

## Structure

```text
context-review/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── agents/
│   └── openai.yaml
└── references/
    ├── question-rubric.md
    └── source-collection.md
```

- `SKILL.md`: 입력 수집, 대형 변경 지도화, AI 자체 확인, 질문 선별과 출력 계약
- `references/question-rubric.md`: 필수 관문, 영향 관점, 우선순위, 안티패턴
- `references/source-collection.md`: immutable snapshot, 플랫폼별 자료 채널, 댓글 ledger와 수집 함정

## Test

```bash
python3 scripts/validate_skills.py --skill context-review
```
