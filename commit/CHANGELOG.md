# Changelog

## 0.3.0

### Added
- 커밋 순서 판단 기준 추가: bisect 안전성, 리뷰 이야기 순서, 단독 revert 검산
- 메시지 품질 기준 추가: "무엇이 달라지는지" 중심, 무의미 동사 요약 금지

## 0.2.0

### Changed
- description에 자연어 트리거 문구 추가
- 전체 diff 일괄 읽기 대신 `--stat` 후 파일 단위 선택 읽기로 변경
- 인터랙티브 `git add -p` 금지, patch + `git apply --cached` 방식으로 대체
- 본문 있는 커밋은 `git commit -F` 사용 명시
- Gemini 보조 분석 블록을 한 줄로 축약

## 0.1.0

### Added
- `/commit` 계획 모드와 `--go` 즉시 실행 모드 정의
- diff 기반 커밋 분할 기준과 Conventional Commits 한글 메시지 규칙 추가
- 위험 변경 감지와 중단 조건 문서화
