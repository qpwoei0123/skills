# Changelog

## 1.4.0

- 에이전트 주도 이의 제기 라운드 추가 (Step 4.5)
- orchestrator.md 이의 처리 절차·제한·판정 기록 형식 추가
- output-templates.md 이의 제기/판정 렌더링 블록 + 예시 추가
- SKILL.md frontmatter에 `version` 필드 추가
- output-templates.md에 `format_version` 마이그레이션 규칙 명시
- CHANGELOG.md 신규 생성

## 1.3.0

- 이슈 출력 포맷 전면 개편: GitHub alerts (`[!WARNING]`, `[!TIP]`) + `diff` 블록
- `<details>` 접기 제거, `---` + 볼드 인용 구분선 방식으로 전환
- 출력 예시 전면 재작성 (npm install → npm ci 시나리오)

## 1.2.0

- orchestrator.md confidence 판정 모순 수정 (source 파일 2개 필수 조건 제거)
- view별 스킵/대체 분석 위임 규칙 명시 (ARCH FSD 없는 레포, DATA 백엔드 레포)

## 1.1.0

- SKILL.md Step 3 observation/rebuttal/query_response 스키마 인라이닝
- publish_issue.py 네트워크 retry + exponential backoff (429/5xx, 최대 3회)
- Retry-After 헤더 지원

## 1.0.0

- 초기 릴리스: 7개 view (SAFE/ARCH/DEP/BUILD/DATA/OPS/DOC)
- view당 Agent A/B/C 3인 구조 + Orchestrator 병합·채점·triage
- 4-criteria triage (impact≥4, urgency≥3, confidence≠low, actionability≥3)
- fingerprint 기반 중복 방지
- publish_issue.py GitHub/GitLab 이슈 발행 + dry-run 지원
