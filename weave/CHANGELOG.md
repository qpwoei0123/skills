# Changelog

## 0.2.1

### Removed
- 분석 순서의 Gemini 보조 분석 블록(설명·예시 명령) 제거

## 0.2.0

### Changed
- description을 트리거 문구 중심으로 보강하고 trim/wow 경계를 명시

### Added
- 같은 이유로 변하는지 판정하는 휴리스틱 한 줄 추가
- 트리거 평가 케이스(`evals/trigger-eval.json`) 추가

## 0.1.0

### Added
- `/weave` 계획 모드와 `--go` 즉시 실행 모드 정의
- 같은 이유로 변하는 코드만 엮는 판단 기준 추가
- 억지 공통화 방지 규칙과 사이드 이펙트 점검 항목 문서화
