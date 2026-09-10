# 관찰·선별·결과 기록

분담 조사나 `result.json` 저장이 필요할 때 읽는다. JSON 호환 필드는 유지하지만 존재하지 않은 리뷰어·반박·라운드를 채우지 않는다.

## 관찰

```json
{
  "agent": "lead",
  "observations": [
    {
      "claim": "확인된 문제",
      "evidence": ["src/path/file.ts:42"],
      "impact_surface": "문제가 발생하는 조건과 영향 범위",
      "next_step": "구체적으로 확인하거나 바꿀 대상과 행동"
    }
  ]
}
```

`agent`는 실제 조사자다. 직접 조사한 경우 `lead`, 분담한 경우 해당 ID를 쓸 수 있다. 위임된 observation에는 점수를 넣지 않는다. 최종 선별자가 실제 근거를 확인해 채점한다.

## 추가 확인

중요한 결론에 상충하는 근거나 공백이 있을 때만 반례 확인·질의·재조사를 한다. 같은 확인을 서로 다른 라운드 이름으로 반복하지 않는다. 추가 확인이 더 이상 판단을 바꿀 수 없으면 남은 불확실성을 기록하고 선별한다.

기존 기록과 호환되는 선택 필드:

- rebuttal: `target_agent`, `target_claim`, `rebuttal`, `evidence`
- query response: `query`, `finding`, `evidence`, `conclusion`
- reexamination: `orchestrator_objection`, `reexamined_files`, `finding`, `conclusion`, `claim_revised`, `comment`

직접 읽은 근거로 claim이 철회·축소·유지됐는지만 기록한다. 근거 없는 이견이나 다른 환경의 반례가 들어왔다는 이유만으로 confidence를 자동 강등하지 않는다. 반대로 반박이 없었다는 사실을 검증으로 취급하지 않는다.

## 병합과 ID

같은 원인과 수정 범위인 관찰을 병합한다. 근거 위치가 같다는 사실만으로 합치지 않는다. `agents`에는 실제 관찰·병합에 기여한 조사자만 넣는다.

`build_finding_id(claim, impact_surface)`를 사용한다. 정규화는 소문자화·앞뒤 공백 제거·내부 공백 collapse이고, 계산은 `SHA1(normalized_claim + "\n" + normalized_impact_surface)[:8]` 앞에 `f-`를 붙이는 방식이다. 최종 claim이 바뀌면 ID를 다시 계산하고 기존 문제의 alias 여부를 확인한다.

## 영향과 시급성

| 점수 | impact | urgency |
|---|---|---|
| 5 | 핵심 비즈니스·인증·보안·데이터 계약에 직접 영향 | 현재 운영 영향이나 재현을 확인함 |
| 4 | 배포·CI·공통 모듈 등 넓은 범위에 영향 | 확인한 다음 배포·신규 환경 조건에서 발생 |
| 3 | 특정 기능에 국한 | 명시한 조건에서 발생 |
| 2 | 비핵심·작은 범위 | 장기적 위험 |
| 1 | 스타일·문서 표현 수준 | 이론적 가능성 |

운영 자료를 읽지 않았으면 정적 코드만으로 production 재현을 주장하지 않는다. 이름에 `auth`, `shared`, `deploy`가 있다는 이유로 impact를 자동 상향하지 않는다.

confidence는 다음처럼 해석한다.

- `high`: 실제 실행 경로·조건과 영향이 직접 근거로 연결되고 중요한 반례를 해소했다.
- `medium`: 문제의 근거는 있지만 일부 환경·영향 조건은 확인하지 못했다. 남은 조건을 명시한다.
- `low`: 핵심 연결이 추정에 의존하거나 중요한 상충 근거가 해결되지 않았다.

## 다음 행동 점수

`compute_actionability(next_step)`가 기존 문자열 heuristic으로 계산한다. 경로 형태 +2, 식별자 형태 +1, CLI token +1, 짧은 문장 형태 +1로 최대 5점이다. 정확한 정규식은 [구현](../scripts/pipeline_contracts.py)을 따른다.

문장 의미를 측정하는 함수가 아니며 경로의 마침표 등도 계산에 영향을 준다. 수동 합계나 그럴듯한 점수 설명을 만들지 않는다. 필요 없는 명령을 추가해서 기준을 통과시키지 않는다.

기본 `triage_pass(impact, urgency, confidence, actionability)`는 순서대로 `low_impact`, `low_urgency`, `low_confidence`, `low_actionability`, `pass`를 반환한다. override가 있는 경우는 [조정 규칙](triage-rules.md)을 따른다.

## result.json

아래는 필드 구조 예시다. 실제 값·ID·점수는 관찰과 helper 결과로 채운다.

```json
{
  "view_id": "BUILD",
  "scan_sha": "abc1234f",
  "mode": "analysis",
  "findings": [
    {
      "id": "f-12345678",
      "claim": "확인된 문제",
      "evidence": ["src/path/file.ts:42"],
      "confidence": "medium",
      "impact": 4,
      "urgency": 3,
      "impact_surface": "확인된 조건과 영향 범위",
      "actionability": {
        "score": 4,
        "next_step": "src/path/file.ts의 `handler`가 쓰는 입력 계약을 확인한다",
        "score_breakdown": "경로 형태 +2, 식별자 형태 +1, 짧은 문장 형태 +1"
      },
      "agents": ["lead"],
      "query": null,
      "reexamination": null,
      "comment_history": [
        {
          "stage": "initial_submission",
          "actor": "리드 리뷰어",
          "role": "BUILD 조사",
          "comment": "직접 확인한 사실 요약",
          "evidence": ["src/path/file.ts:42"],
          "decision": "submitted"
        },
        {
          "stage": "triage_passed",
          "actor": "리드 리뷰어",
          "role": "triage",
          "comment": "근거와 적용한 기준 요약",
          "evidence": [],
          "decision": "passed"
        }
      ]
    }
  ],
  "agent_errors": []
}
```

`comment_history`는 확인 가능한 활동과 판정 요약이다. `initial_submission`, 실제 `triage_passed | triage_skipped | triage_final`을 남기고, `rebuttal | query | objection | reexamination`은 실제 발생한 경우에만 쓴다. 내부 사고 과정이나 가상의 대화를 작성하지 않는다.

오류 항목은 실제 조사자·사유·미검토 범위·이어받은 결과를 기록한다. 단독 조사는 존재하지 않는 리뷰어를 `skipped`나 `failed`로 세지 않는다. 여러 view는 각각 결과를 만들고 중복 문제의 소유 view를 유지한다.
