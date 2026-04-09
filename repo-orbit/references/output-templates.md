# Output Templates

`repo-orbit`의 Step 6 발행 템플릿과 최종 실행 보고 템플릿을 모아 둔 문서다.

## format_version

현재: **`repo-orbit/v2.0.1`**

이슈 본문 footer에 `format_version: repo-orbit/v2.0.1`가 찍힌다.
기존 이슈를 업데이트할 때 footer의 `format_version`이 현재 버전과 다르면, 점수·판정은 유지한 채 **현재 포맷으로 본문을 재작성**한다.

## 목차

- 이슈 제목 형식
- 이슈 본문 템플릿
- 출력 예시
- 발행 필수 파라미터
- 최종 실행 보고

## 이슈 제목 형식

```text
[view: <view_id>] <actionability.next_step 첫 문장> (50자 이내)
```

예:

```text
[view: DEP] .gitlab-ci.yml pnpm 버전 고정
```

## 이슈 본문 템플릿

````markdown
## 문제

{result.json claim}

{result.json impact_surface — 영향 범위를 구체적으로. API 엔드포인트, 빌드 산출물 경로, DB 테이블 등.}

```diff
{문제 코드 before/after — 코드 근거가 없으면 이 블록 생략}
```

`{result.json evidence[0]}` (file:line)

## 조치

{result.json actionability.next_step}

- [ ] {구체적 행동 1}
- [ ] {구체적 행동 2 — 단일 행동이면 1줄만}

---

## 분석 히스토리

#### 1차 제출 · Agent {X} ({역할})

{관찰 직접 화법}

> 근거: `{file:line}`, `{file:line}`

#### 교차 반박 · Agent {Y} ({역할})   ← 발생했을 때만

{반박}

> 근거: `{file:line}`

#### 판정 · Orchestrator

> 점수: impact {n}, urgency {n}, confidence {h/m/l}, actionability {n}

#### 재조사 · Agent {X}   ← 발동 시만

> 근거: `{file:line}` · 결론: `claim_refined` / `claim_withdrawn` / `claim_upheld`

#### 이의 제기 · Agent {X}   ← 발동 시만

{이의 근거와 새 evidence 설명}

> 새 근거: `{file:line}`, `{file:line}`
> 요청: {contested_field} {current_score} → {requested_score}

#### 이의 판정 · Orchestrator   ← 발동 시만

> 판정: `sustained` / `overruled` · 사유: {한 문장}

---

## 이슈화 근거

| 항목 | 점수 | 기준 | 근거 |
|------|------|------|------|
| impact | {n}/5 | ≥ 4 | {한 줄} |
| urgency | {n}/5 | ≥ 3 | {한 줄} |
| confidence | {h/m} | ≠ low | {한 줄} |
| actionability | {n}/5 | ≥ 3 | {한 줄} |

`format_version: repo-orbit/v2.0.1`
`fingerprint: pipeline:{repo}:{view_id}:{finding_id}`
````

작성 규칙:

- `## 문제` 헤더 아래에 claim과 impact_surface를 빈 줄로 구분해 넣는다.
- `diff` 블록은 문제 코드의 before/after를 보여줄 수 있을 때만 쓴다. 코드로 보여줄 수 없으면 생략하고 evidence 경로만 남긴다.
- `## 조치` 헤더 아래에 next_step 한 문장과 체크리스트를 넣는다.
- `## 분석 히스토리`와 `## 이슈화 근거`는 `---` 구분선 뒤에 `##` 헤더로 표시한다.
- GitLab은 `[!WARNING]` / `[!TIP]` 구문을 렌더링하지 않으므로 사용하지 않는다.
- `format_version`은 본문 하단 코드 한 줄로 남긴다.

## 출력 예시

아래는 실제로 발행되는 이슈 본문 예시다.

````markdown
## 문제

CI `before_script`가 `npm install -g pnpm`으로 `pnpm`을 최신 전역 패키지로 설치해, `package.json`의 `packageManager` 고정값 `pnpm@10.14.0`을 우회한다.

이 경로는 모든 CI job의 `pnpm install --frozen-lockfile`에 영향을 주므로, 로컬과 CI의 패키지 매니저 버전이 달라진 상태에서 lockfile 해석과 설치 동작이 어긋날 수 있다.

```diff
-  - npm install -g pnpm
+  - corepack enable
+  - corepack prepare pnpm@10.14.0 --activate
```

`.gitlab-ci.yml:162`

## 조치

`.gitlab-ci.yml:162`의 `npm install -g pnpm`을 `corepack enable && corepack prepare pnpm@10.14.0 --activate`로 바꿔 `package.json:213`의 `packageManager`와 같은 `pnpm` 버전을 쓰게 한다.

- [ ] `.gitlab-ci.yml:162` 전역 `pnpm` 설치 제거
- [ ] `package.json:213`의 `packageManager` 값과 동일한 버전으로 활성화

---

## 분석 히스토리

#### 1차 제출 · Agent A (패키지 버전 고정 + lockfile 상태 분석)

`package.json` 213번째 줄에 `pnpm@10.14.0`이 고정돼 있지만, `.gitlab-ci.yml` 161~163번째 줄은 매번 `npm install -g pnpm` 뒤에 `pnpm install --frozen-lockfile`을 실행한다.

> 근거: `package.json:213`, `.gitlab-ci.yml:161`, `.gitlab-ci.yml:162`, `.gitlab-ci.yml:163`

#### 판정 · Orchestrator

CI 전 job의 의존성 설치 경로에 직접 영향을 주므로 impact 4, 다음 파이프라인부터 바로 재현 가능한 drift(버전 표류)라 urgency 4로 판정했다.

> 점수: impact 4, urgency 4, confidence high, actionability 5

---

## 이슈화 근거

| 항목 | 점수 | 기준 | 근거 |
|------|------|------|------|
| impact | 4/5 | ≥ 4 | 모든 CI job의 `pnpm install --frozen-lockfile` 경로에 직접 영향 |
| urgency | 4/5 | ≥ 3 | 다음 파이프라인부터 repo 고정 버전과 다른 `pnpm`을 받을 수 있음 |
| confidence | high | ≠ low | `package.json:213`과 `.gitlab-ci.yml:161-163` 직접 확인 |
| actionability | 5/5 | ≥ 3 | 파일경로+2, 식별자+1, 명령어+1, 한문장+1 |

`format_version: repo-orbit/v2.0.1`
`fingerprint: pipeline:owner/repo:DEP:E1`
````

### 이의 제기 포함 예시

아래는 에이전트 이의 제기가 인용(sustained)되어 triage를 통과한 경우의 이슈 본문 예시다.

````markdown
## 문제

인증 미들웨어가 `/api/admin/*` 경로에 적용되지 않아 관리자 API가 무인증 접근에 노출된다.

`src/middleware/auth.ts`의 경로 매칭 패턴이 `/api/admin`을 포함하지 않는다. 관리자 전용 엔드포인트(사용자 삭제, 설정 변경)가 인증 없이 호출 가능하다.

```diff
- app.use('/api/user/*', authMiddleware)
+ app.use('/api/user/*', authMiddleware)
+ app.use('/api/admin/*', authMiddleware)
```

`src/middleware/auth.ts:12`

## 조치

`src/middleware/auth.ts:12`의 경로 매칭에 `/api/admin/*` 패턴을 추가한다.

- [ ] `auth.ts:12` 경로 목록에 `/api/admin/*` 추가
- [ ] 관리자 API 엔드포인트에 대한 인증 테스트 작성

---

## 분석 히스토리

#### 1차 제출 · Agent A (라우트 + 미들웨어 분석)

`src/middleware/auth.ts` 12번째 줄의 경로 매칭 배열에 `/api/admin` 패턴이 빠져 있음을 확인했다.

> 근거: `src/middleware/auth.ts:12`

#### 판정 · Orchestrator

인증 누락이지만 admin 경로 사용 빈도가 불명확하여 impact 3으로 판정. triage 기준 미달(impact < 4).

> 점수: impact 3, urgency 4, confidence high, actionability 4

#### 이의 제기 · Agent A

admin API가 사용자 삭제와 시스템 설정 변경을 포함하고 있어 영향 범위가 impact 3보다 넓다.

> 새 근거: `src/api/routes.ts:42`, `src/api/routes.ts:58`
> 요청: impact 3 → 5

#### 이의 판정 · Orchestrator

> 판정: `sustained` · 사유: admin API에 deleteUser, updateSystemConfig이 포함되어 핵심 보안 경로에 해당

---

## 이슈화 근거

| 항목 | 점수 | 기준 | 근거 |
|------|------|------|------|
| impact | 5/5 | ≥ 4 | 관리자 API(사용자 삭제, 시스템 설정) 무인증 노출 |
| urgency | 4/5 | ≥ 3 | 현재 production에서 재현 가능 |
| confidence | high | ≠ low | auth.ts:12 직접 확인 + routes.ts 추가 근거 |
| actionability | 4/5 | ≥ 3 | 파일경로+2, 식별자+1, 한문장+1 |

`format_version: repo-orbit/v2.0.1`
`fingerprint: pipeline:owner/repo:SAFE:E3`
````

## 발행 필수 파라미터

- fingerprint: `pipeline:<repo>:<view_id>:<finding_id}`
- labels: `automation`
- 제목 형식 준수 (50자 이내)
- 본문 footer: `format_version: repo-orbit/v2.0.1`

동일 fingerprint open 이슈 → 최신 본문으로 update.
동일 fingerprint closed 이슈 → reopen하지 않는다. 최종 보고에 "이미 닫힌 이슈" 항목으로 기록하고 사용자에게 안내한다.
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
이미 닫힌 이슈   : N개 (원하시면 새 이슈로 올려드릴 수 있습니다)
────────────────────────────────────────
내일 view     : OPS — 운영 관측성 (토요일)
```
