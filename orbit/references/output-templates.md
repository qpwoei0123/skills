# Output Templates

`orbit`의 Step 6 발행 템플릿과 최종 실행 보고 템플릿을 모아 둔 문서다.

## format_version

현재: **`orbit/v2.3`**

이슈 본문에는 `format_version: orbit/v2.3`이 찍히고, fingerprint footer는 HTML comment 한 줄로 남긴다.
기존 이슈를 업데이트할 때 본문의 `format_version`이 현재 버전과 다르거나 fingerprint footer가 예전 `fingerprint:` 형식이면, 점수·판정은 유지한 채 현재 포맷으로 본문을 재작성한다.

### 마이그레이션 규칙

| 기존 format_version | 처리 |
|---------------------|------|
| `orbit/v1` 또는 없음 | 전체 본문 재작성 |
| `orbit/v2.2` 이하 | 전체 본문 재작성 |
| `orbit/v2.3` + 예전 `fingerprint:` footer | HTML comment footer로 본문 재작성 |
| `orbit/v2.3` + `<!-- orbit-fingerprint: ... -->` footer | 점수 유지, 본문 재작성 생략 |

## 목차

- 이슈 제목 형식
- 심각도 배지 규칙
- 이슈 본문 템플릿
- `알아야 할 개념` 작성 규칙
- severity-aware 선택지
- 출력 예시
- 발행 필수 파라미터
- 최종 실행 보고

## 이슈 제목 형식

발행 스크립트 호환을 위해 제목은 반드시 `[view: <view_id>]`로 시작한다.
제목은 처방보다 상태를 말한다. "분리", "수정", "보강"처럼 즉시 작업을 암시하는 말은 피한다.

```text
[view: <view_id>] <검토할 상태 한 줄> (50자 이내)
```

예:

```text
[view: ARCH] Dbat route module이 page primitive를 함께 들고 있음
[view: DEP] CI pnpm 버전이 고정값을 우회함
```

## 심각도 배지 규칙

이슈 상단 첫 줄에 심각도 배지를 표시한다. 배지는 "작업 강제"가 아니라 "판단 속도"를 높이는 신호다.

| 조건 | 배지 |
|------|------|
| 재현되는 결함, 보안 노출, 데이터 손상, 배포·빌드 차단 | `🔴 즉시 확인` |
| impact = 5 또는 urgency = 5 | `🔴 검토 필요` |
| impact = 4 이상 + urgency = 4 이상 | `🟠 우선 검토` |
| impact = 4 이상 + urgency = 3 | `🟡 검토 제안` |

## 이슈 본문 템플릿

구조 원칙: **결정 메뉴형 검토 보고서**.
이슈는 "해야 할 일"이 아니라 "어떤 판단을 내려야 하는지"를 먼저 보여준다.
다만 재현되는 결함·보안·데이터 손상·빌드 차단처럼 보류가 위험한 이슈는 구조 리스크와 다른 선택지를 쓴다.

````markdown
{배지} · {claim을 쉬운 상태 문장으로 바꾼 한 줄}

## 결정할 것

{읽는 사람이 내려야 할 판단을 한 문장으로 쓴다.}

## 알아야 할 개념

- `{개념}`: {이 이슈 판단에 필요한 만큼만 설명한다.}
- `{개념}`: {모르면 판단이 느려지는 내부 용어만 설명한다.}

## 지금 상태

{확인된 문제 상태를 1~2문장으로 쓴다.}

{구조 리스크면: 바로 고쳐야 하는 버그는 아니지만, {view 표시 이름} 관점에서 검토할 만한 구조 리스크입니다.}
{치명적 결함이면: 현재 재현되거나 노출되는 결함입니다. 보류보다 차단·수정·오탐 확인 중 하나로 판단해야 합니다.}

## 근거

- `{file:line}` {근거를 3~8단어로 설명}
- `{file:line}` {근거를 3~8단어로 설명}
- `{file:line}` {근거를 3~8단어로 설명}

## 판단 포인트

{보고 기준을 넘은 이유를 짧은 문장 2~4개로 쓴다.}

영향 위치가 `{핵심 경로}`입니다.

{의도된 설계라면 어떤 기준으로 예외가 되는지, 아니라면 어떤 위험이 커지는지 쓴다.}

## 다른 리뷰어 의견

{[🔄 변경 리뷰어]/[🧪 커버리지 리뷰어]/[😈 위험 리뷰어] 중 관련 있는 1~2명만 쓴다. 리드 리뷰어는 [🧭 리드 리뷰어]로 표기한다.}

{반박이 있으면 반박을 먼저 쓴다. 반박이 없으면 "반박 근거는 없었습니다"처럼 짧게 쓴다.}

## 선택지

{severity에 맞는 선택지 메뉴를 하나만 고른다.}

<details>
<summary>🧠 브레인스토밍 과정</summary>

1. 관찰 시작: `{view_id}` 관점에서 `{주요 경로}`를 확인했습니다.
2. 초기 가설: `{처음 의심한 구조/결함 상태}`라고 봤습니다.
3. 근거 확인: `{핵심 근거 1}`와 `{핵심 근거 2}`를 확인했습니다.
4. 반박 검토: `{반박이 없었는지, 있었고 어떻게 처리했는지}`를 확인했습니다.
5. 판정: impact `{n}/5`, urgency `{n}/5`, confidence `{high|medium}`, actionability `{n}/5`로 `보고 기준 통과`로 봤습니다.
6. 선택지 도출: `{정리/차단/확인 등 선택지를 고른 이유}` 때문에 현재 메뉴를 제안했습니다.

추적 정보: `pipeline:{repo}:{view_id}:{finding_id}`

</details>

---

`format_version: orbit/v2.3`
<!-- orbit-fingerprint: pipeline:{repo}:{view_id}:{finding_id} -->
````

작성 규칙:

- 섹션 제목은 질문형 또는 짧은 명사형으로 쓴다.
- 한 문단은 1~2문장만 쓴다.
- `## 조치`, `## 완료 기준` 같은 작업 지시형 섹션은 쓰지 않는다.
- `## 결정할 것`은 해결책이 아니라 판단 질문을 쓴다.
- `## 선택지`는 severity에 맞는 메뉴만 쓴다. 재현되는 결함에 `보류한다`를 넣지 않는다. 각 항목은 라벨 앞에 정해진 이모지를 붙인다: ✨ 정리한다 / 🙈 보류한다 / 👾 예외로 둔다 / 🚧 바로 막는다 / 🔧 고친다 / 🤦 오탐으로 닫는다 / 🔍 확인한다 / 🛡️ 예방한다.
- 점수와 추적 정보는 본문 상단에 노출하지 않고 `🧠 브레인스토밍 과정`에 넣는다.
- `🧠 브레인스토밍 과정`은 숨겨진 내부 사고를 쓰지 않는다. 관찰, 가설, 근거, 반박, 판정, 선택지 도출처럼 사용자가 검증할 수 있는 판단 흐름만 요약한다.
- 반박·재조사·이의 제기가 있으면 `## 다른 리뷰어 의견`에 짧게 요약하고, 상세 기록은 별도 `<details>`로 추가할 수 있다.
- 본문에서 리뷰어를 가리킬 때는 역할 이모지를 붙인 태그 형식으로 쓴다: `[🧭 리드 리뷰어]`, `[🔄 변경 리뷰어]`, `[🧪 커버리지 리뷰어]`, `[😈 위험 리뷰어]`. 같은 문단에 같은 리뷰어가 여러 번 나오면 두 번째부터는 태그 없이 짧게 가리켜도 된다.
- GitLab은 `[!WARNING]` / `[!TIP]` 구문을 렌더링하지 않으므로 사용하지 않는다.
- `format_version` 다음 줄에 fingerprint HTML comment footer를 정확히 표시한다.

## `알아야 할 개념` 작성 규칙

이 섹션은 독자가 도메인을 몰라도 판단할 수 있게 만드는 짧은 맥락이다.
항상 쓰는 섹션이지만, 설명할 개념이 없으면 `특별한 도메인 개념은 없습니다.` 한 줄만 쓴다.

- 개념은 0~3개만 쓴다.
- 이 이슈 판단에 필요한 개념만 설명한다.
- 각 설명은 1문장, 최대 2문장이다.
- 일반 개발 용어는 설명하지 않는다.
- 도메인명, 레이어명, 내부 약어, 운영상 위험 개념을 우선 설명한다.
- 설명은 중립적으로 쓴다. "나쁜 구조"처럼 결론을 미리 넣지 않는다.

## severity-aware 선택지

`## 선택지`는 고정 섹션이지만 메뉴는 판정 성격에 따라 바꾼다.

### 구조 리스크

바로 깨지는 버그가 아니라 경계·의존성·운영성·문서 내구성 리스크일 때 사용한다.

```markdown
- ✨ 정리한다: {가능한 정리 방향}
- 🙈 보류한다: 구조 부채로 기록만 합니다.
- 👾 예외로 둔다: {예외로 둘 때 명시해야 할 기준}
```

### 재현되는 결함·보안·데이터 손상·빌드 차단

현재 사용자 영향, 보안 노출, 데이터 손상, 배포 차단, CI 차단처럼 보류가 위험한 이슈일 때 사용한다.
이 메뉴에는 `보류한다`를 넣지 않는다.

```markdown
- 🚧 바로 막는다: {노출 경로, 배포, 기능 플래그, 권한 등을 임시 차단한다.}
- 🔧 고친다: {원인 코드를 수정하고 재발 테스트를 추가한다.}
- 🤦 오탐으로 닫는다: {재현 조건이나 영향 경로가 틀렸음을 확인한 경우에만 닫는다.}
```

### 조건부 리스크

영향은 크지만 특정 배포 설정, 데이터 상태, 사용 플로우에서만 재현될 때 사용한다.

```markdown
- 🔍 확인한다: {재현 조건이나 운영 설정을 확인한다.}
- 🛡️ 예방한다: {조건이 맞을 때 터지지 않도록 가드나 테스트를 둔다.}
- 👾 예외로 둔다: {해당 조건이 실제로 불가능하다는 근거를 남긴다.}
```

## 출력 예시

### 구조 리스크 예시

````markdown
🟡 검토 제안 · Dbat route module이 page navigation primitive를 함께 들고 있음

## 결정할 것

`src/routes/DbatRoutes.tsx`가 route registry만 맡을지, DB 타입과 page navigation primitive까지 소유해도 되는지 정해야 합니다.

## 알아야 할 개념

- `route registry`: URL 경로와 page component를 연결하는 라우팅 선언부입니다. 보통 page 내부 상태나 복원 로직은 직접 소유하지 않습니다.
- `page navigation primitive`: page 이동이나 상태 복원에 재사용되는 route 객체, DB 타입 목록, 마지막 선택값 loader 같은 작은 단위입니다.
- `경계 건강도`: 모듈이 자기 책임 밖의 page/domain 지식을 직접 알기 시작하는지 보는 관점입니다.

## 지금 상태

`src/routes/DbatRoutes.tsx`가 route registry 역할을 넘어서 DB 타입 배열과 test-case route 객체도 함께 export하고 있습니다.

바로 고쳐야 하는 버그는 아니지만, ARCH 관점에서는 route 선언부와 page 상태 관리 경계가 흐려질 수 있는 구조 리스크입니다.

## 근거

- `src/routes/DbatRoutes.tsx:21` DB 타입 배열 export
- `src/routes/DbatRoutes.tsx:63` test-case route export
- `src/pages/instanceList/InstanceListPage.tsx:4` page가 route DB 타입 import
- `src/pages/testCaseGroup/hooks/useTestCaseGroupRoute.ts:4` page hook이 route 객체 재사용
- `src/features/layouts/DbatHeader.tsx:8` header가 page storage helper import

## 판단 포인트

영향 위치는 `/instance-list`, `/test-case-group/$dbType`, 공통 header입니다.

route registry, page 상태 파싱, 마지막 DB 타입 복원이 같은 primitive에 묶여 있습니다. 이 기준이 의도된 설계라면 예외로 둘 수 있지만, 아니라면 route module이 page 상태와 layout 흐름까지 끌어안는 방향으로 커질 수 있습니다.

## 다른 리뷰어 의견

반박 근거는 없었습니다.

[🧪 커버리지 리뷰어]는 test-case-group page와 tab도 같은 route 객체를 다시 읽는다고 봤고, [😈 위험 리뷰어]는 공통 header가 page-local storage helper를 직접 읽는다고 봤습니다.

## 선택지

- ✨ 정리한다: `dbatDbTypes`, `testCaseGroupRoute`, `loadLastDbType`를 route 밖의 중립 shared 모듈로 옮깁니다.
- 🙈 보류한다: 구조 부채로 기록만 합니다. 단 route module이 page 상태 primitive를 계속 소유한다는 점을 인지한 상태로 둡니다.
- 👾 예외로 둔다: Dbat route module이 page navigation primitive까지 소유한다는 기준을 문서로 남깁니다.

<details>
<summary>🧠 브레인스토밍 과정</summary>

1. 관찰 시작: `ARCH` 관점에서 `src/routes/DbatRoutes.tsx`와 page import 경로를 확인했습니다.
2. 초기 가설: route registry가 page navigation primitive까지 함께 소유하고 있을 수 있다고 봤습니다.
3. 근거 확인: DB 타입 배열 export와 page hook의 route 객체 재사용을 확인했습니다.
4. 반박 검토: 반박 근거는 없었고, 다른 리뷰어들도 같은 route 객체 재사용과 page-local storage helper 참조를 확인했습니다.
5. 판정: impact `4/5`, urgency `3/5`, confidence `high`, actionability `5/5`로 `보고 기준 통과`로 봤습니다.
6. 선택지 도출: 바로 깨지는 버그가 아니라 경계 리스크이므로 정리·보류·예외 선택지를 제안했습니다.

추적 정보: `pipeline:owner/repo:ARCH:f-12345678`

</details>

---

`format_version: orbit/v2.3`
<!-- orbit-fingerprint: pipeline:owner/repo:ARCH:f-12345678 -->
````

### 치명적 결함 예시

````markdown
🔴 즉시 확인 · 관리자 API가 인증 없이 호출될 수 있음

## 결정할 것

`/api/admin/*` 경로를 즉시 차단할지, 인증 미들웨어를 바로 적용할지 결정해야 합니다.

## 알아야 할 개념

- `관리자 API`: 사용자 삭제나 시스템 설정 변경처럼 권한이 높은 작업을 수행하는 서버 경로입니다.
- `인증 미들웨어`: 요청자가 로그인했고 필요한 권한을 갖고 있는지 API 실행 전에 확인하는 코드입니다.

## 지금 상태

인증 미들웨어가 `/api/admin/*` 경로에 적용되지 않아 관리자 API가 무인증 접근에 노출됩니다.

현재 재현되거나 노출되는 결함입니다. 보류보다 차단·수정·오탐 확인 중 하나로 판단해야 합니다.

## 근거

- `src/middleware/auth.ts:12` admin 경로 누락
- `src/api/routes.ts:42` 사용자 삭제 API
- `src/api/routes.ts:58` 시스템 설정 변경 API

## 판단 포인트

영향 위치는 `/api/admin/*`입니다.

관리자 권한이 필요한 삭제·설정 변경 경로가 인증 없이 열릴 수 있습니다. 운영 라우팅에서 이 경로가 닿지 않는다는 반례가 없으면 즉시 차단하거나 수정해야 합니다.

## 다른 리뷰어 의견

[😈 위험 리뷰어]는 admin API가 사용자 삭제와 시스템 설정 변경을 포함하므로 impact를 `5`로 올려야 한다고 봤습니다.

[🧭 리드 리뷰어]가 새 근거를 확인했고 이의를 인용했습니다.

## 선택지

- 🚧 바로 막는다: `/api/admin/*` 경로를 임시 차단하거나 관리자 기능 접근을 feature flag로 끕니다.
- 🔧 고친다: 인증 미들웨어에 `/api/admin/*` 패턴을 추가하고 무인증 접근 테스트를 작성합니다.
- 🤦 오탐으로 닫는다: 운영 라우팅에서 `/api/admin/*`가 외부 요청으로 닿을 수 없다는 근거가 있을 때만 닫습니다.

<details>
<summary>🧠 브레인스토밍 과정</summary>

1. 관찰 시작: `SAFE` 관점에서 인증 미들웨어와 관리자 API 경로를 확인했습니다.
2. 초기 가설: 관리자 API가 인증 미들웨어 밖에 있을 수 있다고 봤습니다.
3. 근거 확인: admin 경로 누락과 사용자 삭제·시스템 설정 변경 API를 확인했습니다.
4. 반박 검토: 운영 라우팅에서 접근 불가능하다는 반례는 확인되지 않았습니다.
5. 판정: impact `5/5`, urgency `5/5`, confidence `high`, actionability `5/5`로 `보고 기준 통과`로 봤습니다.
6. 선택지 도출: 보류가 위험한 재현 가능 결함이므로 바로 막기·수정·오탐 확인 선택지를 제안했습니다.

추적 정보: `pipeline:owner/repo:SAFE:f-87654321`

</details>

---

`format_version: orbit/v2.3`
<!-- orbit-fingerprint: pipeline:owner/repo:SAFE:f-87654321 -->
````

### 반박·재조사·이의 제기 예시

반박·재조사·이의 제기가 있었으면 `## 다른 리뷰어 의견` 아래에 짧게 추가한다.

````markdown
## 다른 리뷰어 의견

[😈 위험 리뷰어]는 처음에 영향 범위를 `조건부`로 봤습니다.

[🧭 리드 리뷰어]가 관리자 API 경로를 다시 확인했고, 사용자 삭제와 시스템 설정 변경이 포함된 것을 확인했습니다.

그래서 impact를 `3`에서 `5`로 올렸습니다.

<details>
<summary>검토 기록</summary>

- [😈 위험 리뷰어] 이의: admin API가 사용자 삭제와 시스템 설정 변경을 포함합니다.
- 새 근거: `src/api/routes.ts:42`, `src/api/routes.ts:58`
- [🧭 리드 리뷰어] 판정: `sustained`

</details>
````

## 발행 필수 파라미터

- fingerprint: `pipeline:<repo>:<view_id>:<finding_id>`
- legacy_fingerprint: 같은 repo/view 안에서 같은 finding을 가리키던 과거 fingerprint alias가 있으면 `--legacy-fingerprint`로 전달
- labels: `automation`
- 제목 형식 준수 (50자 이내, `[view: <view_id>]` 접두어 필수)
- 본문 footer: `<!-- orbit-fingerprint: pipeline:owner/repo:VIEW:f-12345678 -->`

동일 fingerprint 또는 같은 repo/view의 legacy fingerprint alias의 open 이슈 → 최신 본문으로 update.
동일 fingerprint 또는 같은 repo/view의 legacy fingerprint alias의 closed 이슈 → reopen하지 않는다. 최종 보고에 "이미 닫힌 이슈" 항목으로 기록하고 사용자에게 안내한다.
다른 view의 동일 claim → update하지 않는다. 최종 보고에 "이미 추적 중" 또는 "이미 닫힌 이슈"로만 기록한다.
발행 실패 항목은 별도 기록하고 나머지는 계속 진행한다.

## 최종 실행 보고

```text
날짜          : YYYY-MM-DD (요일)
레포          : <group>/<project>
view          : DATA — 데이터 구조 & 흐름
리뷰어        : 변경·커버리지·위험 완료  또는  변경·위험 완료 (커버리지 스킵: <이유>)
────────────────────────────────────────
탐색 나침반      : P1(변경) 3개 · P2(미탐색) 5개 · P3(재탐색) 2개 · Skip 8개
관찰 수집        : N개 (리뷰어별 raw 관찰 합계)
채점 후 findings : N개 (중복 병합 후)
Triage 통과      : N개
Triage 스킵      : N개
이미 추적 중     : N개 (다른 view에서 이미 발행된 동일 문제)
발행 성공        : N개
발행 실패        : N개
이미 닫힌 이슈   : N개 (원하시면 새 이슈로 올려드릴 수 있습니다)
────────────────────────────────────────
내일 view     : OPS — 운영 관측성 (토요일)
```

조기 종료 시 보고 형식:

```text
날짜          : YYYY-MM-DD (요일)
레포          : <group>/<project>
view          : DATA — 데이터 구조 & 흐름
────────────────────────────────────────
[skip] 변경사항 없음 — 새로 탐색할 파일도 없습니다.
  last_scan_commit : abc1234f
────────────────────────────────────────
내일 view     : OPS — 운영 관측성 (토요일)
```
