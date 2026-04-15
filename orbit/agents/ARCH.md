# ARCH

경계 건강도 view다.
레이어 방향과 슬라이스 경계가 무너지지 않았는지 본다.

## Agent A — FSD 레이어 의존성 방향 분석

찾을 것:

- `app -> pages -> widgets -> features -> entities -> shared` 방향 준수 여부
- 상위 레이어가 하위 레이어를 건너뛰어 직접 import하는 패턴

## Agent B — 슬라이스 경계 침범 탐지

찾을 것:

- features 간 직접 import 여부
- shared에 비즈니스 로직이 들어간 흔적
- pages/widgets가 feature 내부 구현을 직접 참조하는 경로

## Agent C — 순환 참조 탐지

찾을 것:

- 모듈 간 순환 import 경로
- index barrel로 숨겨진 순환 의존

## 우선 조사 경로

- `src/app`, `src/pages`, `src/widgets`, `src/features`, `src/entities`, `src/shared`
- path alias 설정 파일(`tsconfig`, bundler config)
- barrel export 파일과 공통 index 파일

## finding으로 올릴 최소 조건

- import 방향 위반 또는 순환 경로를 `file:line`으로 적을 수 있다.
- 경계 위반이 한 파일의 예외가 아니라 구조 패턴으로 설명된다.
- `next_step`에서 끊어야 할 import 경로나 옮겨야 할 식별자를 적을 수 있다.

## 문제로 보지 않는 경우

- 테스트 코드 내부의 편의 import
- storybook, mock, fixture 경로만의 의존
- FSD를 채택하지 않은 저장소에서 일반 모듈 import를 FSD 위반으로 단정하는 경우

## FSD 없는 레포 — 일반 모듈 경계 분석

FSD 구조가 없거나 약할 때 A·B를 완전 스킵하지 말고 아래로 대체한다.

### Agent A 대체 (레이어 방향 위반 탐지)

레이어 이름(app/pages/features 등) 대신 **프레젠테이션 → 비즈니스 → 데이터 접근**
방향 위반 여부를 본다.

찾을 것:
- UI 컴포넌트가 DB/쿼리/ORM 레이어를 직접 import하는 경우
- 서비스 레이어가 라우터나 컨트롤러 모듈을 역방향으로 참조하는 경우
- 공통 유틸이 특정 도메인 로직을 직접 끌어오는 경우

예: `components/UserCard.tsx`가 `db/queries.ts`를 직접 import

### Agent B 대체 (public API 경계 침범 탐지)

찾을 것:
- 모듈 내부 구현 파일을 외부에서 직접 import하는 경우 (index.ts 우회)
- 라이브러리/패키지 경계를 무시하고 내부 경로를 참조하는 경우
- 의도적 `private` 표시나 네이밍 컨벤션 (`_internal`, `__` 등)을 무시한 경우

## 축소 조사 규칙

- FSD 구조가 없으면 위 "FSD 없는 레포" 방법으로 A·B를 대체한다.
- 순환은 전체 그래프 대신 공통 barrel과 대표 슬라이스부터 본다.
- 백엔드 레포(서비스/컨트롤러/리포지터리 패턴)는 레이어 방향 위반에 집중한다.

## 스킵 조건

- 단일 파일 프로젝트 → 전체 스킵
- FSD 구조 없음 → A·B를 "FSD 없는 레포" 방식으로 대체 (스킵 아님)

## Orchestrator 메모

- 방향 위반과 순환 참조가 같이 나오면 영향 범위를 더 넓게 본다.
- shared/공통 레이어 오염은 단일 파일보다 시스템 영향으로 평가한다.
- FSD 미사용 레포에서 "FSD 위반"이라는 표현은 쓰지 않는다. "레이어 방향 위반" 또는 "모듈 경계 침범"으로 표현한다.
