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
  - `references/agent-playbook.md`
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

## View별 스킵/대체 분석 위임

각 view의 스킵 조건과 에이전트 대체 분석 규칙은 **`agents/<VIEW>.md`에만** 정의되어 있다.
Orchestrator는 해당 파일을 읽은 뒤 그 지침을 그대로 따른다. 대표 케이스:

- **ARCH view, FSD 없는 레포**: `ARCH.md`의 "FSD 없는 레포 — 일반 모듈 경계 분석" 절로 A·B를 대체.
  FSD 용어("슬라이스", "segment")는 사용하지 않는다.
- **DATA view, 백엔드 레포**: `DATA.md`의 "백엔드 레포 — 데이터 흐름 대체 분석" 절로 A·B·C를 대체.
  프론트엔드 store 용어("selector", "mutation")는 사용하지 않는다.
- 레포 유형 판정 기준과 view별 적용 가이드는 [`references/repo-types.md`](../references/repo-types.md)를 읽는다.

## Step 2 구조 파악 체크리스트

- 진입점 파일과 루트 설정 파일을 먼저 읽는다.
- `src`, `app`, `packages`, `apps`, `services` 같은 상위 디렉터리만 2단계까지 본다.
- generated 디렉터리(`dist`, `.next`, `coverage`)는 source가 아닐 때 우선순위를 낮춘다.
- view 스킵 여부는 "핵심 파일이 전혀 없음"일 때만 결정하고, 축소 조사 가능성부터 확인한다.

## 병합 규칙 상세

- 같은 문제를 다른 파일이 뒷받침하면 하나의 finding으로 묶고 evidence만 확장한다.
- claim이 다르더라도 `impact_surface`와 `next_step`이 같은 방향이면 병합 후보로 본다.
- 반대로 evidence가 같아도 해결 행동이 완전히 다르면 분리한다.
- 병합 뒤 claim은 더 구체적이고 반례에 덜 취약한 표현을 남긴다.

## 재조사 필수 트리거

아래 중 하나면 Step 4.5 재조사를 우선 검토한다.

- evidence 있는 rebuttal이 들어왔는데 claim을 일부만 뒤집는 경우
- source와 generated 산출물이 서로 다른 사실을 가리키는 경우
- 테스트는 있는데 핵심 경로 대응 여부가 불명확한 경우
- 문서와 실제 코드 경로가 충돌하는 경우

## Step 4.5 이의 제기 처리

채점 결과를 에이전트에게 공유한 뒤, triage 기준 미달로 스킵될 finding에 대해 에이전트가 이의를 제기할 수 있다.

### Orchestrator 처리 절차

1. 이의에 `new_evidence`가 없으면 즉시 기각한다 (`overruled`, 사유: "새 근거 없음").
2. `new_evidence`가 있으면 해당 파일:줄을 직접 확인한다.
3. 새 근거가 `contested_field` 점수를 올릴 만한 사실이면 `sustained`, 아니면 `overruled`.
4. `sustained` 시 해당 필드를 재채점하고 triage를 다시 적용한다.
5. `overruled` 시 원래 점수를 유지한다. 판정은 최종이며 추가 항소 없음.

### 제한

- finding당 이의 1회, 에이전트당 이의 1회.
- (a) Orchestrator 주도 재조사와 (b) 에이전트 주도 이의는 같은 finding에 중복 발동하지 않는다.
- 이의 판정은 `comment_history`에 `objection` 이벤트로 기록한다.

### 판정 기록 형식

```json
{
  "finding_id": "E2",
  "objection_by": "A",
  "verdict": "sustained | overruled",
  "reason": "판정 이유 한 문장",
  "revised_score": 4
}
```

`revised_score`는 `sustained`일 때만 의미 있다. `overruled`면 원래 점수를 그대로 둔다.

## confidence 판정 규칙

기준은 SKILL.md Step 4 정의를 따른다 (아래는 동일 내용 요약):

- `high`: 직접 읽은 `file:line` 근거가 있고, evidence를 가진 반박이 없다.
- `low`: 근거가 없거나 추정만 있거나, evidence를 가진 반박이 들어왔다.
- `medium`: high도 low도 아닌 나머지.

경계 케이스 처리:

- source 파일 2개 이상이 같은 claim을 지지하면 `high`를 더 확신할 수 있다 (필수 조건은 아님).
- 영향 범위나 최신성에 해석 여지가 남아 있으면 `medium`으로 유지한다.
- generated 결과(빌드 출력, 로그)만으로 단정하고 source 파일을 직접 읽지 않았으면 `low`다.

## next_step 품질 게이트

- Orchestrator는 triage 전에 `next_step`이 한 문장인지 먼저 확인한다.
- 파일 경로, 식별자, 명령어 중 2개 미만이면 actionability를 낮게 본다.
- "개선한다", "정리한다", "보강한다"만 적힌 문장은 구체화 전까지 통과시키지 않는다.

## 발행 규칙

- 제목 접두어 `[view: <view_id>]`를 바꾸지 않는다.
- footer의 `format_version`과 `fingerprint`를 빼먹지 않는다.
- 동일 fingerprint면 새 이슈보다 update/reopen을 우선한다.

## 보고 규칙

- 서브 에이전트 상태는 완료, 스킵, 실패를 분리해서 적는다.
- `Triage 스킵`은 사유 집계를 유지한다.
- 다음 실행 view를 마지막 줄에 적는다.
