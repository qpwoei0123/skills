# Execution Lifecycle

`orbit`의 Step 3 ~ Step 4.5 상세 규칙을 모아 둔 문서다.
일반 실행에서는 `SKILL.md` core만으로 충분하고, 아래 형식이나 예외가 필요할 때만 이 파일을 읽는다.

## 목차

- 라운드 구조
- 리뷰어 실패/timeout 처리
- observation 형식
- rebuttal 형식
- 리드 리뷰어 질의 형식
- 결과 수집 및 병합 규칙
- 리드 리뷰어 채점 기준
- comment_history 기록 규칙
- result.json 스키마
- Step 4.5 재조사 정책

## 라운드 구조

```text
1라운드: view별 3명 리뷰어가 사실 관찰 제출
2라운드: 결과가 2개 이상일 때 교차 반박 수집
3라운드: 채점 전 의문이 남을 때 리드 리뷰어 질의
4라운드: 리드 리뷰어 병합·채점
4.5라운드: 스킵 finding에 기술적 의문이 있을 때 재조사
5라운드: triage
6라운드: 발행
```

`Step 4.5`는 문서 번호상 뒤에 있어도 실제 실행 순서는 `채점 뒤 → triage 전`이다.

## 리뷰어 실패/timeout 처리

### Timeout SLA

| 라운드 | 리뷰어당 제한 | 비고 |
|--------|----------------|------|
| 1라운드 (observation) | 5분 | 레포 규모에 따라 리드 리뷰어가 2분 연장 가능 |
| 2라운드 (rebuttal) | 2분 | 연장 없음 |
| 3라운드 (query) | 1분 | 연장 없음 |
| 4.5라운드 (재심) | 2분 | 연장 없음 |

리드 리뷰어가 명시적으로 `wait` 신호를 보내지 않으면 위 시간 초과 시 해당 리뷰어를 실패로 처리한다.

### 실패 처리 규칙

리뷰어가 결과를 반환하지 못한 경우:

- 나머지 리뷰어 결과만으로 계속 진행한다. 전체 실행을 중단하지 않는다.
- `coverage-log`의 `agent_errors`에 실패 리뷰어, 사유, 경과 시간을 기록한다.
- 실패한 리뷰어가 맡았던 서브태스크 범위를 최종 보고에 명시한다.
- 결과를 반환한 리뷰어가 1명만 남으면 2라운드 교차 반박은 건너뛴다.
- **전체 리뷰어 실패 시**: 실행을 중단하고 `[error] 모든 리뷰어 실패: <사유>` 보고. 재시도는 하지 않는다.

## observation 형식

리뷰어는 **사실 관찰만** 반환한다. 점수는 절대 붙이지 않는다.

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

## 리드 리뷰어 질의 형식

2라운드 뒤에도 채점 전 사실 관계가 불명확하면 리드 리뷰어가 질의를 던질 수 있다.

발동 예:

- evidence 있는 rebuttal이 claim을 완전히 뒤집는지 불명확할 때
- 서로 모순된 관찰을 병합하기 어려울 때
- 근거 파일을 실제로 누가 읽었는지 확신이 없을 때

질의 전달 형식:

```text
질의 대상: Reviewer <X>
질의 내용: "<구체적인 확인 요청 한 문장>"
확인 요청: <파일 경로 또는 코드 위치>
```

응답 형식:

```json
{
  "agent": "A",
  "query_response": {
    "query": "리드 리뷰어 질의 내용 요약",
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
- 질의는 finding당 최대 1회, 리뷰어당 최대 1회다.

## 결과 수집 및 병합 규칙

### 중복 처리

- 같은 `file:line`을 가리키는 관찰은 하나로 병합한다.
- claim은 더 구체적인 것을 선택한다.
- `next_step`은 더 actionable한 것을 선택한다.
- 병합된 finding의 `agents`에는 원본 리뷰어를 모두 포함한다.
- rebuttal만 제출한 리뷰어는 `agents`에 포함하지 않는다.

### finding ID 부여

- 병합 후 각 finding의 `claim`과 `impact_surface`만으로 ID를 계산한다.
- normalize: `str.lower().strip()` 후 내부 공백을 단일 공백으로 collapse한다.
- 알고리즘: `SHA1(normalized_claim + "\n" + normalized_impact_surface)[:8]` 앞에 `f-`를 붙인다.
- evidence 순서나 다른 finding의 존재 여부는 ID에 영향을 주지 않는다.

## 리드 리뷰어 채점 기준

리드 리뷰어는 리뷰어가 올린 `claim`, `evidence`, `impact_surface`만 보고 점수를 준다.

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
  - 해당 파일을 리뷰어가 직접 읽음
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
  "actor": "변경 리뷰어(A) | 커버리지 리뷰어(B) | 위험 리뷰어(C) | 리드 리뷰어",
  "role": "리뷰어 역할 또는 triage",
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
      "id": "f-12345678",
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
          "actor": "변경 리뷰어(A)",
          "role": "테스트 파일 탐색 + 커버리지 분석",
          "comment": "로그인 핵심 경로에 대응 테스트가 없음을 확인했다.",
          "evidence": ["src/features/auth/ui/LoginForm.tsx:38"],
          "decision": "submitted"
        },
        {
          "stage": "triage_passed",
          "actor": "리드 리뷰어",
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

- `agent_errors`: timeout/오류로 결과를 못 돌려준 리뷰어 기록
- `agents`: 이 finding을 제출했거나 병합에 기여한 리뷰어 목록
- `query`: 3라운드 질의가 있었을 때만 채움
- `reexamination`: Step 4.5 재조사가 있었을 때만 채움
- `comment_history`: 제출, 반박, 질의, 재조사, 최종 판정 이력

## Step 4.5 재심 정책

목적은 이슈를 늘리는 것이 아니라 **실제 건강 상태를 더 정확히 파악하는 것**이다.
채점 직후, triage 전에 두 가지 경로로 재심이 발생할 수 있다. 하나가 발동하면 다른 하나는 발동하지 않는다.

### (a) 리드 리뷰어 주도 재조사

triage에서 스킵될 finding 중, 리드 리뷰어가 기술적으로 의문을 가지면 해당 리뷰어에게 재조사를 건다.

발동하지 않는 경우:

- `low_impact`
- `low_urgency`
- 리드 리뷰어가 별도 기술적 의문이 없는 경우

발동 예:

- "이 분기가 의도적 설계일 수 있지 않나?"
- "이 패턴이 이 레포 표준 관행일 수 있지 않나?"
- "영향 범위가 실제로 이렇게 넓은가?"

재조사 반환 형식:

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

처리 규칙:

- finding당 최대 1회만 재조사한다.
- `claim_refined`: claim/next_step을 수정하고 재채점한다.
- `claim_withdrawn`: finding을 제거하고 `reexam_withdrawn`에 기록한다.
- `claim_upheld`: 원래 claim을 유지한 채 최종 판정한다.

### (b) 리뷰어 주도 이의 제기

리드 리뷰어가 채점 결과를 리뷰어에게 공유한 뒤, 리뷰어가 자신의 finding 점수에 동의하지 않으면 **새 evidence**를 들고 이의를 제기할 수 있다.

발동 조건:

- 리뷰어의 finding이 triage 기준 미달로 스킵 예정일 때
- 원래 observation에 포함하지 않았던 **새 evidence**를 제시할 수 있을 때

이의 제기 형식:

```json
{
  "agent": "A",
  "objection": {
    "finding_id": "f-12345678",
    "contested_field": "impact",
    "current_score": 3,
    "argument": "추가 근거로 영향 범위가 더 넓음을 확인했다",
    "new_evidence": ["src/api/routes.ts:42", "src/middleware/auth.ts:15"],
    "requested_score": 4
  }
}
```

리드 리뷰어 판정 형식:

```json
{
  "finding_id": "f-12345678",
  "objection_by": "A",
  "verdict": "sustained | overruled",
  "reason": "판정 이유 한 문장",
  "revised_score": 4
}
```

처리 규칙:

- 새 evidence가 없는 이의는 즉시 기각한다.
- finding당 이의 1회, 리뷰어당 이의 1회.
- `sustained` (인용): 해당 필드를 재채점하고 triage를 다시 적용한다.
- `overruled` (기각): 원래 점수를 유지한다. 판정은 최종이며 추가 항소 없음.

### 공통

(a)와 (b) 합산 finding당 최대 1회. comment_history에 `reexamination` 또는 `objection` 이벤트로 기록한다.

재심 후 최종 렌더링 형식은 [`output-templates.md`](output-templates.md)를 읽는다.
