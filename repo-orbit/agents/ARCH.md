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

## 스킵 조건

- FSD 구조 없음 → A·B 스킵, C만
- 단일 파일 프로젝트 → 전체 스킵

## Orchestrator 메모

- 방향 위반과 순환 참조가 같이 나오면 영향 범위를 더 넓게 본다.
- shared 오염은 단일 파일보다 시스템 영향으로 평가한다.
