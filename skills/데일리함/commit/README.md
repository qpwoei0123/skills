# .⚡commit

`version: 2.0.0`

현재 변경을 의미 단위로 나누고 저장소 규칙에 맞는 한글 커밋으로 남깁니다.

## Quick Start

```text
$.⚡commit 이번 작업을 의미 단위로 나눠 커밋해줘.
$.⚡commit 커밋하지 말고 분할 계획과 메시지만 보여줘.
```

`$.⚡commit`, `/.⚡commit`은 기본적으로 실행하며 `--go`, `-go`도 지원합니다. "계획만" 같은 명시적 제한은 실행 표기보다 우선합니다.

"PR 준비해줘"나 "커밋하고 PR까지"는 `.⚡ship`이 이 스킬의 커밋 절차를 거쳐 요청한 준비·제출까지 이어갑니다. 무관한 diff는 남길 수 있고, 커밋할 변경이 그 내용에 의존하지 않는지 확인합니다. 저장소의 명시 규칙이 최근 로그와 기본 메시지 형식보다 우선합니다.

## Structure

```text
commit/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── agents/openai.yaml
├── evals/trigger-eval.json
└── scripts/collect_context.sh
```

## Scripts

대상 git 저장소에서 읽기 전용 개요를 수집합니다.

```bash
bash <스킬 디렉터리>/scripts/collect_context.sh
```

## Test

```bash
python3 scripts/validate_skills.py --skill .⚡commit
```
