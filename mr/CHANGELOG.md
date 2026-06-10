# Changelog

## 0.3.0

### Added
- 본문 판단 기준 추가: 접근 이유와 버린 대안, 리뷰 포인트 명시, 기계적 변경 묶기
- 셀프 리뷰 단계 추가: 생성 전 리뷰어 시점 재검토, 발견 문제 공개, 대형 diff 분할 제안

## 0.2.0

### Changed
- description에 자연어 트리거 문구 추가
- 분석 단계에 기존 열린 MR/PR 확인 추가, 중복 생성 방지를 중단 조건에 포함
- 본문 임시 파일을 고정 경로 대신 `mktemp`로 생성

## 0.1.0

### Added
- `/mr` 계획 모드와 `--go` 즉시 실행 모드 정의
- GitHub PR과 GitLab MR을 모두 draft로 생성하는 실행 계약 추가
- Conventional 형식 제목, 주변 MR/PR 스타일 참고, 레포 템플릿 기반 본문 규칙 추가
- dirty worktree와 draft 미보장 상황의 중단 조건 문서화
