# Output Templates

`repo-orbit`의 Step 6 발행 템플릿과 최종 실행 보고 템플릿을 모아 둔 문서다.

## 목차

- 이슈 제목 형식
- 이슈 본문 템플릿
- 발행 필수 파라미터
- 최종 실행 보고

## 이슈 제목 형식

```text
[view: <view_id>] <actionability.next_step 첫 문장> (50자 이내)
```

예:

```text
[view: DATA] src/features/order/model/store.ts 중복 상태 제거
```

## 이슈 본문 템플릿

```markdown
## [view: {view_id}] {제목}

> {result.json claim}

## 왜 중요한가

> {result.json impact_surface}

## 근거

> {result.json evidence[0]} (file:line)

## 지금 할 일

> {result.json actionability.next_step}

## 분석 히스토리

이 finding이 거쳐온 전체 흐름을 시간순으로 기록한다.
각 단계의 주체가 자신의 관찰·판단·반론을 직접 코멘트로 남긴다.

### N. 1차 제출 · Agent {X} ({서브태스크 역할})

{Agent의 첫 관찰을 직접 화법으로}

> 근거: `{file:line}`, `{file:line}`

### N. 교차 반박 · Agent {Y} ({서브태스크 역할})   ← 발생했을 때만

{Agent Y의 반박}

> 근거: `{file:line}`

### N. 1차 판정 · Orchestrator

{초기 채점과 판정 이유}

> 판정: `passed` 또는 `skipped ({사유})`
> 점수: impact {n}, urgency {n}, confidence {h/m/l}, actionability {n}

### N. Orchestrator 반박   ← 재조사 발동 시만

{기술적 의문 제기}

### N. 재조사 · Agent {X} ({서브태스크 역할})   ← 재조사 발동 시만

{재조사 결과}

> 근거: `{file:line}`
> 결론: `claim_refined` / `claim_withdrawn` / `claim_upheld`

### N. 최종 판정 · Orchestrator   ← 재조사 발동 시만

{재조사 후 최종 판단}

> 판정: `passed` 또는 `skipped (확정)`
> 점수 변화: `{예: actionability 2 → 4}`

## 이슈화 근거

| 항목 | 점수 | 기준치 | 판정 | 비고 |
|------|------|--------|------|------|
| impact | {n}/5 | ≥ 4 | ✅ | {왜 이 점수인지 한 줄} |
| urgency | {n}/5 | ≥ 3 | ✅ | {왜 이 점수인지 한 줄} |
| confidence | {high/medium} | ≠ low | ✅ | {근거 파일 또는 직접 확인 여부} |
| actionability | {n}/5 | ≥ 3 | ✅ | {적용된 rule 나열} |

`format_version: repo-orbit/v2`
`fingerprint: pipeline:{repo}:{view_id}:{finding_id}`
```

작성 규칙:

- 첫 화면에서는 `왜 중요한가`, `근거`, `지금 할 일`이 먼저 보여야 한다.
- `왜 중요한가`와 `근거`를 섞지 않는다.
- `왜 중요한가`에는 가능하면 실제 산출물 경로(`dist/**`, `.next/` 등)를 쓴다.
- 분석 히스토리는 접지 않는다.
- `format_version`은 본문 하단 코드 한 줄로 남긴다.
- 상단 카드 구조나 필수 섹션 구성이 바뀌면 `format_version`을 올린다.

## 발행 필수 파라미터

- fingerprint: `pipeline:<repo>:<view_id>:<finding_id>`
- labels: `automation`
- 제목 형식 준수 (50자 이내)
- 본문 footer: `format_version: repo-orbit/v2`

동일 fingerprint open 이슈 → 최신 본문으로 update.
동일 fingerprint closed 이슈 → reopen + update.
발행 실패 항목은 별도 기록하고 나머지는 계속 진행한다.

## 최종 실행 보고

```text
날짜          : YYYY-MM-DD (요일)
레포          : <group>/<project>
view          : DATA — 데이터 구조 & 흐름
서브 에이전트 : A·B·C 완료  또는  A·C 완료 (B 스킵: <이유>)
────────────────────────────────────────
관찰 수집        : N개 (에이전트별 raw 관찰 합계)
채점 후 findings : N개 (중복 병합 후)
Triage 통과      : N개
Triage 스킵      : N개
발행 성공        : N개
발행 실패        : N개
────────────────────────────────────────
내일 view     : OPS — 운영 관측성 (토요일)
```
