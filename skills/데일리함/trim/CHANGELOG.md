# Changelog

## 0.4.1

### Added
- OpenAI 스킬 메타데이터 `agents/openai.yaml` 추가

### Fixed
- `--go` rollback이 git index를 건드리지 않고 trim 델타만 복원해 기존 staged·unstaged·untracked 변경을 보존하도록 계약 수정
- rollback 중 동시 사용자 변경을 덮을 수 있으면 자동 복원 대신 중단·보고하도록 보강

## 0.4.0

### Added
- weave 스킬을 흡수 통합: 후보를 "덜어내기"와 "엮기" 두 갈래로 분류, 엮기 판정 기준은 `references/weave-criteria.md`로 분리
- 사용자가 범위를 지목하면 diff 없이도 그 범위의 흩어진 패턴을 다루는 대상 범위 추가
- `evals/trigger-eval.json` 신설 (경계 케이스 포함 10건)

### Changed
- description에서 과광범위 트리거 "정리해줘"·"다듬어줘" 제거, "중복 합쳐줘"·"공통화해줘" 승계, 내장 simplify 우선순위와 wow·code-review 경계 명시
- 위험도(낮음/보통/높음)와 근거 등급(1/2/3) 이원 체계를 근거 등급 단일 척도로 통합
- `--go` 스냅샷을 `git diff HEAD`(staged 포함) + untracked 백업으로 보강하고 mktemp 경로 사용, 복원 절차를 tracked/untracked로 분기
- 빈 diff·비git 저장소 중단 조건과 base 결정 규칙 명시

### Removed
- 중복 로직·중복 상수 항목을 덜어내기 목록에서 엮기 후보로 이동

## 0.3.2

### Removed
- 분석 순서의 Gemini 보조 분석 언급 제거

## 0.3.1

### Changed
- 단순화 포인트·상태/구조 기준을 스택 중립 원리 먼저, React/TS는 괄호 예시로 재서술해 백엔드·CLI·라이브러리 diff에도 같은 판단표가 적용되게 함

## 0.3.0

### Added
- 동작 보존 근거 3등급제 추가: `--go`는 기계적 보장·전수 확인 등급만 적용
- 동치처럼 보이지만 동작이 바뀌는 함정 체크리스트 추가
- 판단 기준을 줄 수에서 "읽는 사람의 개념 수"로 명시

## 0.2.0

### Changed
- description에 자연어 트리거 문구 추가
- `--go` 적용 전 `pre-trim.patch` 스냅샷 의무화, 복원 절차 구체화
- 단순화 포인트가 React/TS 예시 기준임을 명시
- Gemini 보조 분석 블록을 한 줄로 축약

## 0.1.0

### Added
- `/trim` 계획 모드와 `--go` 즉시 실행 모드 정의
- diff 중심 단순화 포인트 탐지 기준 추가
- 동작 보존, 검증 전후 비교, 중단 조건 문서화
