---
name: repo-orbit
description: >
  레포지터리를 요일별 고정 view(SAFE/ARCH/DEP/BUILD/DATA/OPS/DOC)로 분석하고
  기준을 통과한 finding만 GitHub 또는 GitLab 이슈로 자동 발행하는 파이프라인 스킬.
  프롬프트에서 직접 `$repo-orbit`처럼 호출해 사용한다.
---

# repo-orbit

7개 관점(view)을 요일마다 하나씩 고정 배정해 레포를 분석하고, 기준을 통과한 finding만 이슈로 발행한다.
각 view는 **3개의 서브 에이전트**를 병렬 실행하고, **Orchestrator**가 사실 관찰을 병합해 채점한다.

이 문서는 **core 규칙**만 담는다.
실제 view별 에이전트 지시는 `agents/`, JSON 스키마와 템플릿은 `references/`, 반복 실행 로직은 `scripts/`에서 읽는다.

## 디렉터리 구조

```text
repo-orbit/
├── SKILL.md
├── agents/
│   ├── orchestrator.md
│   ├── SAFE.md
│   ├── ARCH.md
│   ├── DEP.md
│   ├── BUILD.md
│   ├── DATA.md
│   ├── OPS.md
│   └── DOC.md
├── references/
│   ├── execution-lifecycle.md
│   ├── triage-rules.md
│   ├── output-templates.md
│   └── coverage-log-schema.md
└── scripts/
    ├── publish_issue.py
    └── test_publish_issue.py
```

## Quick Start

```text
$repo-orbit
```

## 요일별 View 배정

| 요일 | view_id | 관점 | 핵심 질문 |
|------|---------|------|-----------|
| 월 | `SAFE`  | 변경 안전성 | 핵심 흐름에 테스트·검증 게이트가 있는가 |
| 화 | `ARCH`  | 경계 건강도 | FSD 레이어 의존성이 올바른 방향인가, 슬라이스 경계가 지켜지는가 |
| 수 | `DEP`   | 의존성/설정 안정성 | 환경변수·버전 고정이 분산·중복되지 않는가 |
| 목 | `BUILD` | 빌드/배포 재현성 | 로컬과 CI가 같은 경로를 타는가 |
| 금 | `DATA`  | 데이터 구조 & 흐름 | 데이터가 단일 출처에서 예측 가능한 경로로 흐르는가 |
| 토 | `OPS`   | 운영 관측성 | 장애 시 로그·알림·복구 경로를 빠르게 찾을 수 있는가 |
| 일 | `DOC`   | 지식 내구성 | 문서·의사결정 기록·온보딩 경로가 남아 있는가 |

## 실행 방식

이 스킬은 별도 옵션 없이 실행한다.
오늘 날짜 기준으로 view 하나를 선택해 Step 1~6을 순서대로 수행한다.

## 파이프라인 핵심

1. **View 결정**: 오늘 날짜 기준으로 기본 view를 선택한다.
2. **레포 구조 파악**: 상위 트리와 설정 파일을 확인해 스킵 조건을 판정한다.
3. **사실 관찰 수집**: 선택된 view의 서브 에이전트 3개를 병렬 실행해 사실 관찰만 받는다.
4. **병합·채점**: 중복 관찰을 병합하고 Orchestrator가 impact/urgency/confidence/actionability를 부여한다.
5. **Triage**: 통과 조건을 만족하는 finding만 이슈화 대상으로 고른다.
6. **발행**: triage 통과 finding마다 `scripts/publish_issue.py`를 호출해 이슈를 생성·업데이트한다.

`Step 4.5` 재조사는 **초기 채점 뒤, triage 전에** 선택적으로 발생한다.
정확한 흐름은 [`references/execution-lifecycle.md`](references/execution-lifecycle.md)를 읽는다.

## Step 1 — View 결정

기본 매핑은 아래와 같다.

```text
월 SAFE
화 ARCH
수 DEP
목 BUILD
금 DATA
토 OPS
일 DOC
```

- 날짜·요일은 항상 확인하되, 요일과 view가 달라도 오류가 아니다.
- Step 1 완료 후 최소한 아래를 보고한다.

```text
날짜 : YYYY-MM-DD (요일)
view : DATA — 데이터 구조 & 흐름
```

## Step 2 — 레포 구조 파악

Orchestrator가 직접 아래를 확인한다.
목적은 **서브태스크 스킵 조건 판단**이다.

**브랜치 기준:** 파일 트리 확인 전 반드시 `git fetch`를 먼저 실행한다. 원격 최신 상태를 기준으로 분석한다.
기본값은 `origin/main` 또는 `origin/master`의 최신 HEAD다.

- 파일 트리 상위 2단계
- `package.json`, `vite.config.*`, `tsconfig.*`
- CI 설정 파일 존재 여부 (`.github/`, `.gitlab-ci.yml` 등)
- 상태관리 라이브러리 사용 여부
- 테스트 파일 존재 여부 (`*.test.*`, `*.spec.*`)
- FSD 구조 여부 (`src/app/`, `src/pages/`, `src/features/` 등)

처리 원칙은 아래와 같다.

- 파일 트리 확인 자체가 불가능하면 실행을 중단하고 `[error] 레포 접근 실패: <사유>`를 남긴다.
- 일부 설정 파일만 없는 경우는 있는 것만 읽고 계속 진행한다.
- 선택된 view에 해당하는 파일이 없어 모든 서브태스크가 스킵되면 findings `0`으로 정상 종료한다.

## Step 3 — 사실 관찰 수집

선택된 view의 서브태스크 3개를 병렬 실행한다.
공통 제어 규칙은 [`agents/orchestrator.md`](agents/orchestrator.md)를, view별 역할과 스킵 조건은 `agents/<VIEW>.md`를 읽는다.

핵심 원칙:

- Orchestrator는 **선택된 view 파일 하나만** 읽고 서브 에이전트를 띄운다.
- 서브 에이전트는 **사실 관찰만** 반환한다.
- 점수(impact, urgency, confidence, actionability)는 서브 에이전트가 붙이지 않는다.
- 관찰에는 직접 읽은 `file:line` 근거가 있어야 한다.
- 1라운드 결과가 2개 이상이면 2라운드 교차 반박을 진행한다.
- 채점 전 의문이 남으면 3라운드 Orchestrator 질의를 선택적으로 수행한다.

정확한 형식은 [`references/execution-lifecycle.md`](references/execution-lifecycle.md)를 읽는다.

- observation JSON
- rebuttal JSON
- query response JSON
- 에이전트 실패/timeout 처리
- 병합 규칙과 finding ID 부여 규칙

## Step 4 — 병합·채점

Orchestrator가 수집된 관찰을 병합하고 finding 단위로 채점한다.

핵심 원칙:

- 같은 `file:line`을 가리키는 관찰은 하나로 병합한다.
- 병합된 finding의 `agents`에는 원본 에이전트를 모두 남긴다.
- finding ID는 `evidence[0]` 경로 알파벳순으로 정렬한 뒤 `E1`, `E2`, `E3`로 부여한다.

채점 기준의 핵심은 아래와 같다.

### impact

| 점수 | 기준 |
|------|------|
| 5 | 핵심 비즈니스 경로 또는 보안/인증에 직접 영향 |
| 4 | 배포·CI·공통 모듈 등 넓은 범위에 영향 |
| 3 | 특정 기능이나 페이지에 국한 |
| 2 | 단일 컴포넌트 또는 비핵심 경로 |
| 1 | 코드 스타일·주석 수준 |

### urgency

| 점수 | 기준 |
|------|------|
| 5 | 현재 production에서 재현 가능 |
| 4 | 다음 배포 또는 신규 환경에서 즉시 재현 가능 |
| 3 | 조건부 재현 |
| 2 | 장기적 리스크 |
| 1 | 이론적 리스크 |

### confidence

- `high`: 직접 읽은 `file:line` 근거가 있고, evidence를 가진 반박이 없다
- `low`: 근거가 없거나 추정만 있거나, evidence를 가진 반박이 들어왔다
- `medium`: 위 두 조건 사이의 나머지

`comment_history`, `result.json`, 재조사(`Step 4.5`)의 정확한 스키마는 [`references/execution-lifecycle.md`](references/execution-lifecycle.md)를 읽는다.

## Step 5 — Triage

모든 finding에 아래 기준을 순서대로 적용한다.
하나라도 스킵 조건에 걸리면 이슈화하지 않는다.

### 통과 조건

```text
1) impact >= 4 AND urgency >= 3
2) confidence != low
3) actionability.score >= 3
```

### actionability.score

아래 규칙의 합으로 계산한다. 재량 채점은 없다.

| 규칙 | 점수 |
|------|------|
| next_step에 파일 경로 포함 | +2 |
| next_step에 식별자 포함 | +1 |
| next_step에 CLI 명령어 포함 | +1 |
| next_step이 한 문장 이하 | +1 |

최대 점수는 `5`, 이슈화 최소 점수는 `3`이다.

### 자동 스킵 사유

| 조건 | skip_reason |
|------|-------------|
| impact < 4 | `low_impact` |
| urgency < 3 | `low_urgency` |
| confidence == "low" | `low_confidence` |
| actionability.score < 3 | `low_actionability` |

triage 통과 finding이 0개여도 실패가 아니다.
override 옵션, 재검토 트리거, 상세 예시는 [`references/triage-rules.md`](references/triage-rules.md)를 읽는다.

## Step 6 — 발행

triage 통과 finding마다 `python3 scripts/publish_issue.py`를 호출해 발행한다.
직접 `curl`과 `grep`으로 JSON을 파싱하지 않는다.

### 발행 전 사전 확인 (Preflight)

| 항목 | 확인 방법 | 없을 때 |
|------|-----------|---------|
| 레포 URL | 프롬프트에서 추출 | 사용자에게 입력 요청 |
| `scripts/publish_issue.py` | 파일 존재 여부 확인 | 실행 중단 + `[error] publish_issue.py 없음` |
| Python 3 | `python3 --version` | 실행 중단 + `[error] Python 3 필요` |
| 인증 토큰 | 환경변수 → `~/.repo-orbit/auth.json` 순으로 탐색 | 사용자에게 입력 요청. 없으면 manual payload로 종료 가능 |

### 토큰 로드

`~/.repo-orbit/auth.json`을 읽은 뒤 해당 플랫폼 토큰을 추출한다.
환경변수 `GITHUB_TOKEN` / `GITLAB_TOKEN`이 있으면 우선 사용한다.
토큰이 없으면 사용자에게 직접 요청하고, 응답이 없으면 스크립트의 manual payload를 그대로 출력한다.

`auth.json` 구조는 `references/coverage-log-schema.md` 참조.

### 플랫폼 감지

| 레포 URL 패턴 | 플랫폼 | API Base |
|--------------|--------|----------|
| `github.com` 포함 | GitHub | `https://api.github.com` |
| 그 외 | GitLab | `auth.json`의 `gitlab_base_url` 또는 레포 URL scheme+host |

### Fingerprint 중복 체크

`scripts/publish_issue.py`가 아래를 모두 담당한다.

- 페이지네이션 처리
- JSON 구조 파싱
- 동일 fingerprint open 이슈 update
- 동일 fingerprint closed 이슈 reopen + update
- 토큰/네트워크 오류 시 manual payload 반환

Orchestrator는 중복 체크용 임시 `grep` 로직을 만들지 않는다.

### 호출 예시

```bash
python3 scripts/publish_issue.py \
  --repo-url  https://github.com/owner/repo \
  --title     "[view: BUILD] 로컬과 CI 빌드 경로 일치" \
  --body-file /tmp/repo-orbit-issue.md \
  --fingerprint "pipeline:owner/repo:BUILD:E1" \
  --labels    automation
```

### 핵심 규칙

- 제목은 50자 이내로 자른다.
- 이슈 본문 하단에 `format_version: repo-orbit/v2`와 `fingerprint`를 반드시 포함한다.
- 동일 fingerprint open 이슈 → 제목·본문·label을 현재 포맷으로 update.
- 동일 fingerprint closed 이슈 → reopen + update.
- update·reopen 모두 발행 성공 건수에 포함한다.
- 발행 실패 항목이 있어도 나머지 finding은 계속 진행한다.
- 스크립트가 `manual_required`를 반환하면 title/body/labels/fingerprint를 그대로 최종 보고에 포함한다.

`format_version`은 상단 카드 구조나 필수 섹션 구성이 바뀔 때만 올린다.
이슈 본문 템플릿과 최종 실행 보고 템플릿은 [`references/output-templates.md`](references/output-templates.md)를 읽는다.

## 출력 계약

실행 종료 후 최소한 아래 항목은 항상 보고한다.

- 날짜
- 레포
- view
- 서브 에이전트 상태
- raw 관찰 수
- 병합 후 finding 수
- triage 통과/스킵 수
- 발행 성공/실패 수
- 내일 view

정확한 포맷은 [`references/output-templates.md`](references/output-templates.md)를 읽는다.

## Guide

필요한 문서만 읽고, 무조건 전부 읽지 않는다.

- [`agents/orchestrator.md`](agents/orchestrator.md)
  - Step 2~6 공통 제어 순서와 어떤 파일을 언제 읽는지 필요할 때
- `agents/<VIEW>.md`
  - 선택된 view의 서브태스크와 스킵 조건이 필요할 때
- [`references/execution-lifecycle.md`](references/execution-lifecycle.md)
  - observation/rebuttal/query/result.json/comment_history/reexamination의 정확한 형식이 필요할 때
- [`references/triage-rules.md`](references/triage-rules.md)
  - triage override, 재검토 트리거, 상세 스킵 정책이 필요할 때
- [`references/output-templates.md`](references/output-templates.md)
  - 이슈 본문과 최종 실행 보고 템플릿이 필요할 때
- [`references/coverage-log-schema.md`](references/coverage-log-schema.md)
  - coverage-log 저장 위치와 스키마, 에이전트 실패 기록 방식이 필요할 때
- [`scripts/publish_issue.py`](scripts/publish_issue.py)
  - 발행 로직, fingerprint 처리, manual payload 형식이 필요할 때

## 최소 규칙

- 근거 없는 claim을 만들지 않는다.
- 서브 에이전트는 점수 없이 사실만 반환한다.
- Orchestrator만 병합, 채점, triage, 발행 판단을 한다.
- Step 3에서는 선택된 view 파일만 읽는다.
- fingerprint는 `pipeline:<repo>:<view_id>:<finding_id>`를 유지한다.
- 동일 fingerprint open 이슈는 스킵하지 않고 최신 `format_version`으로 update한다.
- 동일 fingerprint closed 이슈는 reopen + update한다.
