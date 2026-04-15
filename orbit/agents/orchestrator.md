# Orchestrator

`orbit`의 공통 제어 문서다.
Orchestrator는 이 파일을 기본으로 읽고, Step 3에서 **선택된 view 파일 하나만** 추가로 읽는다.

## 역할

- 오늘 실행할 view를 결정하고 해당 view의 메모리 파일을 로드한다.
- `git diff last_scan_commit..HEAD`로 변경 파일을 파악하고 탐색 우선순위를 계산한다.
- 선택된 view의 Agent A/B/C를 병렬 실행하고 탐색 우선순위를 함께 전달한다.
- 관찰을 병합하고 점수화하고 triage를 적용한다.
- `scripts/publish_issue.py`로 이슈를 발행한다.
- 실행 완료 후 view 메모리 파일을 갱신한다.

## 실행 순서

1. 날짜와 옵션을 보고 실행 view를 정한다.
2. `~/.orbit/<group>/<project>/<VIEW>.json`을 읽어 `last_scan_commit`과 `explored_files`, `known_findings`를 가져온다. 파일이 없으면 최초 실행으로 처리한다. **나머지 6개 view 메모리 파일도 읽어** 전체 `status == "open"` finding의 `claim_summary`를 컨텍스트에 보관한다 (중복 발행 방지용). 파일이 없는 view는 건너뛴다.
3. `git fetch` 후 파일 트리와 핵심 설정 파일을 확인한다. `git diff <last_scan_commit>..HEAD --name-only`로 `changed_files`를 구한다.
4. 탐색 우선순위를 계산한다 (아래 "탐색 나침반" 절 참고). 변경도 없고 미탐색도 없으면 조기 종료.
5. `agents/<VIEW>.md` 하나만 읽는다.
6. 거기 적힌 Agent A/B/C 역할과 스킵 조건대로 서브 에이전트를 띄운다. 탐색 우선순위 목록을 에이전트 지시에 포함한다.
7. 관찰이 2개 이상이면 교차 반박을 수집한다.
8. 사실 관계가 불명확하면 질의를 최대 1회 던진다.
9. 병합·채점·triage 후 통과 finding만 발행 대상으로 고른다. triage 통과 finding이 Step 2에서 보관한 기존 open claim_summary와 **실질적으로 같은 문제**이면 발행하지 않고 최종 보고에 `[이미 추적 중: <기존 fingerprint>]`로 표시한다.
10. `python3 scripts/publish_issue.py`를 finding마다 호출한다.
11. view 메모리 파일을 갱신한다 (`last_scan_commit`, `explored_files`, `known_findings`, `run_history`).

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

## 탐색 나침반

메모리에서 읽은 `explored_files`와 `changed_files`를 조합해 아래 우선순위로 탐색 목록을 만든다.

```
Priority 1 — changed_files 중 이 view에 관련된 파일
  → 반드시 분석한다. thorough로 탐색.

Priority 2 — explored_files에 없는 파일 중 이 view에 관련된 파일
  → 한 번도 탐색하지 않은 곳. thorough로 탐색.

Priority 3 — explored_files에 있고 depth=surface이며 last_explored가 오래된 파일
  → 이전에 트리만 봤거나 오래 됐으면 이번에 thorough 재탐색.

Skip — explored_files에 있고 depth=thorough이며 changed_files에 없는 파일
  → 건드리지 않는다.
```

이 목록을 에이전트에 전달할 때 형식 예시:

```
[탐색 우선순위]
Priority 1 (변경됨): .gitlab-ci.yml, package.json
Priority 2 (미탐색): src/config/env.ts, .env.example
Priority 3 (surface 재탐색): Dockerfile
Skip: src/utils/format.ts (thorough, 변경 없음)
```

에이전트는 Skip 파일을 탐색 범위에 포함하지 않는다.
Skip 파일에서 observation이 올라오면 Orchestrator가 근거를 확인하지 않고 낮은 우선순위로 처리한다.

### 조기 종료 판정

아래 조건을 **둘 다** 만족하면 에이전트 spawn 없이 조기 종료한다.

- `changed_files = []` (last_scan_commit 이후 변경 없음)
- Priority 2 + Priority 3에 해당하는 파일이 없음 (미탐색·오래된 surface 없음)

조기 종료 시 `run_history`에 항목을 남기고 종료 보고를 출력한다.

## Step 2 구조 파악 체크리스트

- 진입점 파일과 루트 설정 파일을 먼저 읽는다.
- `src`, `app`, `packages`, `apps`, `services` 같은 상위 디렉터리만 2단계까지 본다.
- generated 디렉터리(`dist`, `.next`, `coverage`)는 source가 아닐 때 우선순위를 낮춘다.
- view 스킵 여부는 "핵심 파일이 전혀 없음"일 때만 결정하고, 축소 조사 가능성부터 확인한다.
- 탐색 나침반 우선순위 목록을 완성한 뒤 에이전트를 spawn한다.

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

기준은 SKILL.md Step 4를 따른다. 경계 케이스:

- 영향 범위나 최신성에 해석 여지가 남아 있으면 `medium`으로 유지한다.
- generated 결과(빌드 출력, 로그)만으로 단정하고 source 파일을 직접 읽지 않았으면 `low`다.

## next_step 품질 게이트

- Orchestrator는 triage 전에 `next_step`이 한 문장인지 먼저 확인한다.
- 파일 경로, 식별자, 명령어 중 2개 미만이면 actionability를 낮게 본다.
- "개선한다", "정리한다", "보강한다"만 적힌 문장은 구체화 전까지 통과시키지 않는다.

## 발행 규칙

- 제목 접두어 `[view: <view_id>]`를 바꾸지 않는다.
- footer의 `format_version`과 `fingerprint`를 빼먹지 않는다.
- 동일 fingerprint open 이슈면 새 이슈 대신 update를 우선한다.
- 동일 fingerprint closed 이슈는 재오픈하지 않는다. `skipped_closed`로 기록하고 최종 보고에 포함한다.

## 메모리 갱신 규칙

발행 완료 후 view 메모리 파일을 갱신한다.

1. `last_scan_commit` → 현재 HEAD 커밋 해시
2. `explored_files` → 이번 실행에서 탐색한 파일마다 `depth`와 `last_explored` 갱신. 새 파일이면 추가.
3. `known_findings` → 새 finding은 `open`으로 추가. changed_files에 포함된 영역의 `closed` finding은 코드가 바뀐 만큼 상태 재검토 (재현 가능성 있으면 `open` 복귀 가능). `suppressed` finding은 재검토하지 않고 그대로 유지한다.
4. `run_history` → 새 entry prepend. 11번째 이상 제거. `changed_files`, `observations_collected`, `findings_after_merge`, `triage_passed`, `issued` 포함.

### suppressed finding 처리

triage 전에 `known_findings`에서 `status == "suppressed"`인 fingerprint를 확인한다.
해당 fingerprint와 동일한 finding이 이번 실행에서 올라오면 이슈화하지 않고 조용히 스킵한다.
최종 보고에도 포함하지 않는다.

사용자가 `--suppress <fingerprint>` 옵션으로 요청하면:
- 해당 fingerprint가 `known_findings`에 있으면 `status`를 `"suppressed"`로 변경하고 메모리 파일을 저장한다.
- 없으면 `"suppressed"` 상태로 신규 추가한다 (미래 발견에 대비).
- 처리 결과를 사용자에게 확인 메시지로 보고한다.

조기 종료 시 `run_history` entry는 아래 값으로 기록하고, `last_scan_commit`은 **업데이트하지 않는다** (변경이 없었으므로 다음 실행도 같은 diff 기준을 유지해야 한다).

```json
{
  "run_at": "<ISO 8601 타임스탬프>",
  "commit": "<현재 HEAD>",
  "diff_base": "<이전 last_scan_commit>",
  "changed_files": [],
  "observations_collected": 0,
  "findings_after_merge": 0,
  "triage_passed": 0,
  "issued": 0
}
```

## 보고 규칙

- 서브 에이전트 상태는 완료, 스킵, 실패를 분리해서 적는다.
- `Triage 스킵`은 사유 집계를 유지한다.
- 탐색 나침반 결과를 간단히 표시한다: Priority 1/2/3 파일 수, Skip 파일 수.
- 다음 실행 view를 마지막 줄에 적는다.
