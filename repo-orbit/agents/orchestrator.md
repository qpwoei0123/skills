# Orchestrator

`repo-orbit`의 공통 제어 문서다.
Orchestrator는 이 파일을 기본으로 읽고, Step 3에서 **선택된 view 파일 하나만** 추가로 읽는다.

## 역할

- 오늘 실행할 view를 결정한다.
- 레포 구조를 훑어 스킵 조건 판단에 필요한 사실을 모은다.
- 선택된 view의 Agent A/B/C를 병렬 실행한다.
- 관찰을 병합하고 점수화하고 triage를 적용한다.
- `scripts/publish_issue.py`로 이슈를 발행한다.

## 실행 순서

1. 날짜와 옵션을 보고 실행 view를 정한다.
2. `git fetch` 후 파일 트리와 핵심 설정 파일을 확인한다.
3. `agents/<VIEW>.md` 하나만 읽는다.
4. 거기 적힌 Agent A/B/C 역할과 스킵 조건대로 서브 에이전트를 띄운다.
5. 관찰이 2개 이상이면 교차 반박을 수집한다.
6. 사실 관계가 불명확하면 질의를 최대 1회 던진다.
7. 병합·채점·triage 후 통과 finding만 발행 대상으로 고른다.
8. `python3 scripts/publish_issue.py`를 finding마다 호출한다.

## 읽는 문서

- 항상 읽기:
  - `SKILL.md`
  - `agents/orchestrator.md`
- 선택적으로 읽기:
  - `agents/<VIEW>.md`
  - `references/execution-lifecycle.md`
  - `references/triage-rules.md`
  - `references/output-templates.md`
  - `references/coverage-log-schema.md`

## 제어 규칙

- 선택되지 않은 다른 view 파일은 읽지 않는다.
- 서브 에이전트에게는 점수 계산을 맡기지 않는다.
- 스킵은 spawn하지 않은 경우만 뜻한다. timeout이나 오류는 `agent_errors`로 기록한다.
- finding ID는 병합 후 `evidence[0]` 기준으로 부여한다.
- `manual_required`가 나오면 실패로 버리지 말고 수동 발행 자료로 최종 보고에 포함한다.

## 발행 규칙

- 제목 접두어 `[view: <view_id>]`를 바꾸지 않는다.
- footer의 `format_version`과 `fingerprint`를 빼먹지 않는다.
- 동일 fingerprint면 새 이슈보다 update/reopen을 우선한다.

## 보고 규칙

- 서브 에이전트 상태는 완료, 스킵, 실패를 분리해서 적는다.
- `Triage 스킵`은 사유 집계를 유지한다.
- 다음 실행 view를 마지막 줄에 적는다.
