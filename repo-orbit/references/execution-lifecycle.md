# Execution Lifecycle

`repo-orbit`의 Step 3 ~ Step 4.5 상세 규칙을 모아 둔 문서다.
일반 실행에서는 `SKILL.md` core만으로 충분하고, 아래 형식이나 예외가 필요할 때만 이 파일을 읽는다.

## 목차

- 라운드 구조
- 에이전트 실패/timeout 처리
- observation 형식
- rebuttal 형식
- Orchestrator 질의 형식
- 결과 수집 및 병합 규칙
- Orchestrator 채점 기준
- comment_history 기록 규칙
- result.json 스키마
- Step 4.5 재조사 정책

## 라운드 구조

```text
1라운드: view별 3개 에이전트가 사실 관찰 제출
2라운드: 결과가 2개 이상일 때 교차 반박 수집
3라운드: 채점 전 의문이 남을 때 Orchestrator 질의
4라운드: Orchestrator 병합·채점
4.5라운드: 스킵 finding에 기술적 의문이 있을 때 재조사
5라운드: triage
6라운드: 발행
```

`Step 4.5`는 문서 번호상 뒤에 있어도 실제 실행 순서는 `채점 뒤 → triage 전`이다.

## 에이전트 실패/timeout 처리

에이전트가 결과를 반환하지 못한 경우:

- 나머지 에이전트 결과만으로 계속 진행한다. 전체 실행을 중단하지 않는다.
- `coverage-log`의 `agent_errors`에 실패 에이전트와 사유를 기록한다.
- 실패한 에이전트가 맡았던 서브태스크 범위를 최종 보고에 명시한다.
- 결과를 반환한 에이전트가 1개만 남으면 2라운드 교차 반박은 건너뛴다.

## observation 형식

서브 에이전트는 **사실 관찰만** 반환한다. 점수는 절대 붙이지 않는다.

```json
{
  "agent": "A",
  "observations": [
    {
      "claim": "발견된 문제 한 문장",
      "evidence": ["src/features/auth/ui/LoginForm.tsx:38"],
      "impact_surface": "영향받는 범위 설명",
      "next_step": "구체적인 다음 행동 한 문장"
    }
  ]
}
```

규칙:

- `evidence`는 직접 읽은 `file:line`만 적는다.
- 추정, 가능성, 간접 인용은 `confidence low` 후보가 된다.
- `impact`, `urgency`, `confidence`, `actionability`는 observation에 넣지 않는다.

## rebuttal 형식

교차 반박은 자신이 직접 읽은 파일/코드와 충돌하는 claim에 한정한다.
단순한 불일치 느낌이나 취향 차이는 rebuttal이 아니다.

```json
{
  "agent": "B",
  "rebuttals": [
    {
      "target_agent": "A",
      "target_claim": "반박 대상 claim 요약",
      "rebuttal": "반박 근거 한 문장",
      "evidence": ["반박을 뒷받침하는 파일:줄"]
    }
  ]
}
```

처리 규칙:

- evidence 없는 rebuttal은 참고만 하고 confidence에는 반영하지 않는다.
- evidence 있는 rebuttal이 하나라도 있으면 해당 claim의 confidence는 `low` 후보가 된다.

## Orchestrator 질의 형식

2라운드 뒤에도 채점 전 사실 관계가 불명확하면 Orchestrator가 질의를 던질 수 있다.

발동 예:

- evidence 있는 rebuttal이 claim을 완전히 뒤집는지 불명확할 때
- 서로 모순된 관찰을 병합하기 어려울 때
- 근거 파일을 실제로 누가 읽었는지 확신이 없을 때

질의 전달 형식:

```text
질의 대상: Agent <X>
질의 내용: "<구체적인 확인 요청 한 문장>"
확인 요청: <파일 경로 또는 코드 위치>
```

응답 형식:

```json
{
  "agent": "A",
  "query_response": {
    "query": "Orchestrator 질의 내용 요약",
    "finding": "직접 확인한 결과 한 문장",
    "evidence": ["확인한 파일:줄"],
    "conclusion": "claim 유지 | claim 수정 필요 | claim 철회"
  }
}
```

처리 규칙:

- `claim 유지`: 원래 채점을 계속 진행한다.
- `claim 수정 필요`: claim/next_step을 수정한 뒤 채점을 진행한다.
- `claim 철회`: finding을 제거하고 `queries_withdrawn`에 기록한다.
- 질의는 finding당 최대 1회, 에이전트당 최대 1회다.

## 결과 수집 및 병합 규칙

### 중복 처리

- 같은 `file:line`을 가리키는 관찰은 하나로 병합한다.
- claim은 더 구체적인 것을 선택한다.
- `next_step`은 더 actionable한 것을 선택한다.
- 병합된 finding의 `agents`에는 원본 에이전트를 모두 포함한다.
- rebuttal만 제출한 에이전트는 `agents`에 포함하지 않는다.

### finding ID 부여

- 병합 후 `evidence[0]` 파일 경로 기준 알파벳순으로 정렬한다.
- 순서대로 `E1`, `E2`, `E3`를 부여한다.
- evidence 없는 finding은 맨 뒤에 붙인다.

## Orchestrator 채점 기준

Orchestrator는 서브 에이전트가 올린 `claim`, `evidence`, `impact_surface`만 보고 점수를 준다.

### impact

```text
5 — 핵심 비즈니스 경로 또는 보안/인증에 직접 영향
4 — 배포·CI·공통 모듈 등 넓은 범위에 영향
3 — 특정 기능이나 페이지에 국한
2 — 단일 컴포넌트 또는 비핵심 경로
1 — 코드 스타일·주석 수준
```

### urgency

```text
5 — 현재 production에서 재현 가능
4 — 다음 배포 또는 신규 환경에서 즉시 재현 가능
3 — 조건부 재현
2 — 장기적 리스크
1 — 이론적 리스크
```

### confidence

```text
high:
  - evidence에 file:line이 1개 이상 있음
  - 해당 파일을 에이전트가 직접 읽음
  - evidence 있는 rebuttal이 없음

low:
  - evidence가 없거나 추정/가능성 표현뿐임
  - evidence 있는 rebuttal이 들어옴

medium:
  - high도 low도 아님
```

`actionability.score`는 `SKILL.md` Step 5 공식 그대로 계산한다.

## comment_history 기록 규칙

각 주체가 **해당 시점에 직접** 한 사건만 기록한다.

최소 포함 이벤트:

- `initial_submission`
- `triage_passed` 또는 `triage_skipped` 또는 `triage_final`

선택 포함 이벤트:

- `rebuttal`
- `query`
- `objection`
- `reexamination`

```json
{
  "stage": "initial_submission | rebuttal | query | objection | reexamination | triage_passed | triage_skipped | triage_final",
  "actor": "Agent A | Agent B | Agent C | Orchestrator",
  "role": "에이전트 역할 또는 triage",
  "comment": "사람이 읽을 한 문장 코멘트",
  "evidence": ["file:line"],
  "decision": "submitted | rebutted | queried | objected | claim_refined | claim_withdrawn | claim_upheld | passed | skipped | null"
}
```

## result.json 스키마

```json
{
  "view_id": "SAFE",
  "findings": [
    {
      "id": "E1",
      "claim": "발견된 문제 한 문장",
      "evidence": ["src/features/auth/ui/LoginForm.tsx:38"],
      "confidence": "high",
      "impact": 5,
      "urgency": 4,
      "impact_surface": "영향받는 범위 설명",
      "actionability": {
        "score": 3,
        "next_step": "구체적인 다음 행동 한 문장",
        "score_breakdown": "파일경로+2, 한문장+1"
      },
      "agents": ["A", "C"],
      "query": null,
      "reexamination": null,
      "comment_history": [
        {
          "stage": "initial_submission",
          "actor": "Agent A",
          "role": "테스트 파일 탐색 + 커버리지 분석",
          "comment": "로그인 핵심 경로에 대응 테스트가 없음을 확인했다.",
          "evidence": ["src/features/auth/ui/LoginForm.tsx:38"],
          "decision": "submitted"
        },
        {
          "stage": "triage_passed",
          "actor": "Orchestrator",
          "role": "triage",
          "comment": "impact 5, urgency 4, confidence high, actionability 3으로 triage 통과 처리했다.",
          "evidence": [],
          "decision": "passed"
        }
      ]
    }
  ],
  "agent_errors": []
}
```

필드 요약:

- `agent_errors`: timeout/오류로 결과를 못 돌려준 에이전트 기록
- `agents`: 이 finding을 제출했거나 병합에 기여한 에이전트 목록
- `query`: 3라운드 질의가 있었을 때만 채움
- `reexamination`: Step 4.5 재조사가 있었을 때만 채움
- `comment_history`: 제출, 반박, 질의, 재조사, 최종 판정 이력

## Step 4.5 재조사 정책

목적은 이슈를 늘리는 것이 아니라 **실제 건강 상태를 더 정확히 파악하는 것**이다.
triage에서 스킵된 finding 중, Orchestrator가 기술적으로 의문을 가지면 재조사를 건다.

### 발동하지 않는 경우

- `low_impact`
- `low_urgency`
- Orchestrator가 별도 기술적 의문이 없는 경우

### 발동 예

- "이 분기가 의도적 설계일 수 있지 않나?"
- "이 패턴이 이 레포 표준 관행일 수 있지 않나?"
- "영향 범위가 실제로 이렇게 넓은가?"

### 재조사 반환 형식

```json
{
  "agent": "B",
  "reexamination": {
    "orchestrator_objection": "Dockerfile의 .env.production은 배포용 의도적 분기일 수 있다",
    "reexamined_files": ["Dockerfile:4", "Dockerfile:9"],
    "finding": "직접 재조사로 확인한 새 사실 한 문장",
    "conclusion": "claim_refined | claim_withdrawn | claim_upheld",
    "claim_revised": "정교화된 claim",
    "comment": "재조사 결과를 이슈 히스토리에 남길 코멘트"
  }
}
```

### 처리 규칙

- finding당 최대 1회만 재조사한다.
- `claim_refined`: claim/next_step을 수정하고 재채점한다.
- `claim_withdrawn`: finding을 제거하고 `reexam_withdrawn`에 기록한다.
- `claim_upheld`: 원래 claim을 유지한 채 최종 판정한다.

재조사 후 최종 렌더링 형식은 [`output-templates.md`](output-templates.md)를 읽는다.
