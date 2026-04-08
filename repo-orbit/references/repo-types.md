# Repo Types

Step 2에서 레포 구조를 파악한 뒤 **레포 유형**을 판정하고, 각 view 에이전트에게 전달한다.
유형 판정은 스킵 조건 결정과 view별 "대체 조사 경로" 선택에 직접 영향을 준다.

## 유형 판정 기준

아래 신호를 보고 가장 가까운 유형을 하나 고른다.

| 신호 | 유형 |
|------|------|
| `package.json` + `src/app/`, `src/pages/`, `src/features/` | FSD Frontend |
| `package.json` + React/Vue/Svelte + `src/` (FSD 아님) | Generic Frontend |
| `package.json` + Express/Fastify/NestJS 또는 `src/routes/`, `src/controllers/` | Node Backend |
| `pyproject.toml`, `setup.py`, `requirements.txt` + `src/` 또는 모듈 디렉터리 | Python Backend |
| `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle` | Go/Rust/Java |
| `packages/`, `apps/`, `services/` 아래 여러 독립 패키지 | Monorepo |
| 단일 Docker Compose + 여러 서비스 디렉터리 | Microservices |
| `package.json` + `index.ts` + `dist/` + `types/` (앱 없음) | Library/Package |
| `bin/` 또는 CLI 진입점 + 최소 UI | CLI Tool |
| `_site/`, `public/`, 정적 HTML + no JS framework | Static Site |

판정이 어려우면 "Generic"으로 두고 조사한다.

---

## 유형별 view 적용 가이드

### FSD Frontend (기본)

모든 view가 SKILL.md 기본 설명대로 동작한다.

### Generic Frontend

- **ARCH**: A·B를 "일반 모듈 경계 분석"(ARCH.md 참고)으로 대체. FSD 용어 쓰지 않음.
- **DATA**: 상태관리 라이브러리 유무 확인 후 없으면 query cache·컴포넌트 state 중심.
- 나머지 view: 동일.

### Node Backend

- **ARCH**: 레이어 방향(controller → service → repository/model) 위반에 집중. FSD 스킵.
- **DATA**: "백엔드 레포" 모드(DATA.md 참고) — N+1, 검증 레이어, 응답 형태 일관성.
- **SAFE**: 라우터 대신 진입점(Express `app.js`, 미들웨어 등) 중심 테스트 게이트 확인.
- **OPS**: 로그 레벨 일관성 + APM(Datadog/OpenTelemetry) 설정 확인.

### Python Backend

- **ARCH**: `controllers/`, `services/`, `repositories/` 또는 Django apps 간 방향 위반.
- **DEP**: `requirements.txt` vs `pyproject.toml` 중복, 버전 범위(`>=`, `~=`) 과도 사용.
- **DATA**: Pydantic/Marshmallow 스키마와 실제 DB 모델 불일치.
- **BUILD**: `Dockerfile`, CI 환경 변수, `python -m` vs `uvicorn` 실행 경로 차이.

### Go / Rust / Java

- **ARCH**: Go는 패키지 순환 import. Rust는 `pub use` 과도 노출. Java는 레이어 패키지 방향.
- **SAFE**: 단위 테스트(`_test.go`, `#[cfg(test)]`, JUnit) 핵심 경로 커버 여부.
- **DEP**: Go — `go.sum` 고정 여부. Rust — `Cargo.lock` 커밋 여부. Java — BOM 버전 고정.
- **DATA**: A·B 스킵. C만: 직렬화 레이어(serde, Jackson, protobuf) 일관성.

### Monorepo

- **Step 2 추가 확인**: 패키지 관리자(`pnpm workspaces`, `nx`, `turborepo`, `Lerna`) 감지.
- **ARCH**: 패키지 간 의존 방향 (`apps/*` → `packages/*` 방향) 위반.
- **DEP**: 루트 `package.json` vs 각 패키지 `package.json` 버전 충돌.
- **BUILD**: 루트 CI 스크립트와 개별 패키지 빌드 명령 불일치.
- **DOC**: 각 패키지 README 존재 여부 + 전체 온보딩 문서.
- **나머지 view**: 영향 범위가 가장 큰 패키지 1-2개를 선택해 집중 조사.

### Microservices

- **Step 2 추가 확인**: Docker Compose/Helm 차트, API Gateway, 서비스 디렉터리 목록.
- **ARCH**: 서비스 간 직접 함수 호출 대신 이벤트/HTTP 경계 위반 여부.
- **BUILD**: 서비스별 Dockerfile 베이스 이미지 버전 일관성. 공통 base image 유무.
- **OPS**: 분산 트레이싱(OpenTelemetry, Zipkin) 설정. 서비스별 로그 형식 불일치.
- **SAFE**: 각 서비스 핵심 엔드포인트 테스트 커버 여부 (E2E 포함).
- **DATA**: 서비스 간 공유 DB 스키마 또는 이벤트 계약(event contract) 일관성.

### Library / Package

- **ARCH**: public API (`index.ts` / `lib.rs` / `__init__.py`) 외 내부 경로 직접 노출 여부.
- **SAFE**: 모든 public API의 단위 테스트 + 타입 테스트 존재 여부.
- **DOC**: 각 exported 함수·클래스의 JSDoc/rustdoc/docstring 존재 여부.
- **DEP**: peer dependency 범위가 과도하게 제한적이거나 느슨한 경우.
- **DATA**: 스킵 (상태 없음). 단, serialization 레이어가 있으면 C만.
- **OPS**: 스킵 (서버 없음). 대신 bundle size, tree-shaking 가능 여부 확인.

### CLI Tool

- **ARCH**: 커맨드 파서 → 비즈니스 로직 → I/O 레이어 방향 위반.
- **SAFE**: 각 커맨드 핵심 경로 단위 테스트 존재 여부.
- **OPS**: stderr/stdout 분리, exit code 일관성, 에러 메시지 명확성.
- **DATA**: A·B 스킵. C만: 입력 검증 레이어 일관성.
- **DOC**: `--help` 텍스트와 README 커맨드 설명 일치 여부.

### Static Site

- **DATA**: 전체 스킵 (상태 없음).
- **ARCH**: 스킵 (모듈 없음).
- **BUILD**: 빌드 도구(`hugo`, `gatsby`, `eleventy`) 버전 고정, CI 배포 스크립트 일관성.
- **OPS**: 404 처리, robots.txt, CSP 헤더 설정.
- **DOC**: 콘텐츠 파일의 frontmatter 스키마 일관성.
- **SAFE·DEP**: 정적 에셋 의존성(CDN URL, 외부 스크립트) 확인.

---

## Orchestrator 메모

- 유형 판정은 Step 2에서 1회만 하고, 이후 모든 step에서 동일한 유형을 유지한다.
- 판정 결과를 Step 1 보고에 추가한다: `유형 : Monorepo (turborepo)`.
- 유형이 불명확하면 "Generic"으로 두되, 각 view에서 발견한 단서로 보완한다.
- 유형에 따라 스킵되는 서브태스크는 `agents_skipped`에 기록한다.
