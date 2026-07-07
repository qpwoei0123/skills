# Changelog

## 0.5.1

### Changed
- description을 "새 커밋을 만드는 요청"으로 좁히고 amend·되돌리기·로그 조회 제외와 mr 위임을 명시 (오발동 차단)
- `--go` 검증 단계를 "계획의 실행 예정에 밝힌 명령만, 변경 파일에 대응하는 lint/test로 한정"으로 구체화
- 중단 조건의 "파일 삭제"를 "현재 요청과 무관해 보이는 대량 파일 삭제"로 완화 (죽은 코드 정리 커밋에서 불필요한 중단 제거)
- 빈 변경 시 "커밋할 변경 없음" 보고 후 종료, 사용자 staged 상태 의도 존중, pre-commit hook 실패 시 `--no-verify` 우회 금지 규칙 추가
- `collect_context.sh`: `git status -sb`로 브랜치 표시, untracked 출력 50개 캡
- trigger-eval에 amend·revert·로그 조회·복합 요청 경계 케이스 5건 보강

## 0.5.0

### Added
- 읽기 전용 커밋 개요를 한 번에 수집하는 `scripts/collect_context.sh` 추가

### Removed
- 분석 순서에서 Gemini 보조 분석 언급 제거

## 0.4.0

### Added
- `--go` 실행 모드에 계획 모드와 짝이 맞는 실행 결과 보고 템플릿 추가
- 트리거 정확도 점검용 `evals/trigger-eval.json` 추가

## 0.3.2

### Changed
- 커밋 승인과 `--go`가 다음 사용자 요청으로 이월되지 않도록 세션 경계 규칙 추가
- 커밋 완료 후 자동 커밋 intent를 종료하고 후속 작업에서는 명시 요청을 다시 받도록 명시

## 0.3.1

### Changed
- 최근 로그를 단순 조회로 끝내지 않고 참고 커밋 3~5개와 채택한 메시지 스타일을 확정하도록 강화
- 본문 있는 커밋이 보이면 주변 본문 구조도 확인하도록 추가
- 커밋 계획에 참고한 최근 커밋과 채택한 메시지 스타일을 보고하도록 추가

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
