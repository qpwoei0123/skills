# Output Templates

`repo-orbit`의 Step 6 발행 템플릿과 최종 실행 보고 템플릿을 모아 둔 문서다.

## format_version

현재: **`repo-orbit/v2`**

이슈 본문 footer에 `format_version: repo-orbit/v2`가 찍힌다.
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
[view: DEP] .github/workflows/ci.yml npm install → npm ci 교체
```

## 이슈 본문 템플릿

```markdown
> [!WARNING]
> {result.json claim}
>
> {result.json impact_surface — 영향 범위를 구체적으로. API 엔드포인트, 빌드 산출물 경로, DB 테이블 등.}

```diff
{문제 코드 before/after — 코드 근거가 없으면 이 블록 생략}
```

`{result.json evidence[0]}` (file:line)

> [!TIP]
> {result.json actionability.next_step}
>
> - [ ] {구체적 행동 1}
> - [ ] {구체적 행동 2 — 단일 행동이면 1줄만}

---

> **분석 히스토리**

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

> **이슈화 근거**

| 항목 | 점수 | 기준 | 근거 |
|------|------|------|------|
| impact | {n}/5 | ≥ 4 | {한 줄} |
| urgency | {n}/5 | ≥ 3 | {한 줄} |
| confidence | {h/m} | ≠ low | {한 줄} |
| actionability | {n}/5 | ≥ 3 | {한 줄} |

`format_version: repo-orbit/v2`
`fingerprint: pipeline:{repo}:{view_id}:{finding_id}`
```

작성 규칙:

- `[!WARNING]` 블록 안에 claim과 impact_surface를 함께 넣는다. 빈 줄(`>`)로 구분한다.
- `diff` 블록은 문제 코드의 before/after를 보여줄 수 있을 때만 쓴다. 코드로 보여줄 수 없으면 생략하고 evidence 경로만 남긴다.
- `[!TIP]` 블록 안에 next_step 한 문장과 체크리스트를 함께 넣는다.
- `##` 제목은 사용하지 않는다. alert 블록과 코드 블록이 시각적 구조를 대신한다.
- 분석 히스토리와 이슈화 근거는 `---` 구분선 뒤에 펼쳐서 보여준다.
- `format_version`은 본문 하단 코드 한 줄로 남긴다.

## 출력 예시

아래는 실제로 발행되는 이슈 본문 예시다.

```markdown
> [!WARNING]
> CI 워크플로우가 `npm install`을 사용해 lockfile을 무시하고 있어, 로컬과 CI 빌드 간 패키지 버전이 달라질 수 있다.
>
> `npm install`은 `package-lock.json`이 있어도 최신 호환 버전을 새로 받을 수 있다. CI에서만 재현되는 빌드 실패가 이 차이에서 비롯되며, 배포 아티팩트의 재현성이 보장되지 않는다.

```diff
- run: npm install
+ run: npm ci
```

`.github/workflows/ci.yml:14`

> [!TIP]
> `.github/workflows/ci.yml:14`의 `npm install`을 `npm ci`로 교체한다.
>
> - [ ] `ci.yml:14` `npm install` → `npm ci` 변경
> - [ ] `package-lock.json`이 `.gitignore`에서 제외되어 있는지 확인

---

> **분석 히스토리**

#### 1차 제출 · Agent B (CI 설정 + lockfile 상태 분석)

`.github/workflows/ci.yml` 14번째 줄에서 `npm install`이 사용되고 있음을 직접 확인했다. `package-lock.json`은 존재하지만 이 커맨드로는 무시된다.

> 근거: `.github/workflows/ci.yml:14`, `package-lock.json:1`

#### 판정 · Orchestrator

CI 전 단계에 걸쳐 재현성에 영향을 주므로 impact 4로 판정. 다음 PR 병합 시점부터 즉시 재현 가능하므로 urgency 3.

> 점수: impact 4, urgency 3, confidence high, actionability 4

---

> **이슈화 근거**

| 항목 | 점수 | 기준 | 근거 |
|------|------|------|------|
| impact | 4/5 | ≥ 4 | CI 전 단계 재현성에 직접 영향 |
| urgency | 3/5 | ≥ 3 | 다음 배포 시 즉시 재현 가능 |
| confidence | high | ≠ low | ci.yml:14 직접 확인 |
| actionability | 4/5 | ≥ 3 | 파일경로+2, 식별자+1, 한문장+1 |

`format_version: repo-orbit/v2`
`fingerprint: pipeline:owner/repo:DEP:E1`
```

### 이의 제기 포함 예시

아래는 에이전트 이의 제기가 인용(sustained)되어 triage를 통과한 경우의 이슈 본문 예시다.

```markdown
> [!WARNING]
> 인증 미들웨어가 `/api/admin/*` 경로에 적용되지 않아 관리자 API가 무인증 접근에 노출된다.
>
> `src/middleware/auth.ts`의 경로 매칭 패턴이 `/api/admin`을 포함하지 않는다. 관리자 전용 엔드포인트(사용자 삭제, 설정 변경)가 인증 없이 호출 가능하다.

```diff
- app.use('/api/user/*', authMiddleware)
+ app.use('/api/user/*', authMiddleware)
+ app.use('/api/admin/*', authMiddleware)
```

`src/middleware/auth.ts:12`

> [!TIP]
> `src/middleware/auth.ts:12`의 경로 매칭에 `/api/admin/*` 패턴을 추가한다.
>
> - [ ] `auth.ts:12` 경로 목록에 `/api/admin/*` 추가
> - [ ] 관리자 API 엔드포인트에 대한 인증 테스트 작성

---

> **분석 히스토리**

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

> **이슈화 근거**

| 항목 | 점수 | 기준 | 근거 |
|------|------|------|------|
| impact | 5/5 | ≥ 4 | 관리자 API(사용자 삭제, 시스템 설정) 무인증 노출 |
| urgency | 4/5 | ≥ 3 | 현재 production에서 재현 가능 |
| confidence | high | ≠ low | auth.ts:12 직접 확인 + routes.ts 추가 근거 |
| actionability | 4/5 | ≥ 3 | 파일경로+2, 식별자+1, 한문장+1 |

`format_version: repo-orbit/v2`
`fingerprint: pipeline:owner/repo:SAFE:E3`
```

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
