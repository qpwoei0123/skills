# Changelog

## 0.1.1

### Added

- `package.json`/`package-lock.json` 추가: Node.js 20+, `tsx`, `playwright` 버전과 캡처/smoke 명령 고정
- 트리거·비트리거 5개씩으로 구성한 `evals/trigger-eval.json` 추가
- OpenAI 스킬 메타데이터 `agents/openai.yaml` 추가
- batch 입력과 submit 응답 본문의 실패 경계를 고정하는 Node 회귀 테스트 추가

### Fixed

- 캡처 CLI의 top-level await를 `main()`으로 대체해 CJS 변환 환경에서도 실행 가능하게 수정
- Figma submit timeout·non-2xx·응답 본문 오류를 실패로 처리하고, 부분 실패가 있으면 프로세스를 non-zero로 종료
- 빈 batch와 비어 있는 capture ID/URL을 입력 오류로 처리
- Claude 전용 플러그인 CLI 전제를 제거하고 호스트 도구를 Figma capability에 매핑하는 계약으로 변경

## 0.1.0

### Added

- 작업 계약 4칸(Figma 권한 / 원본 화면 / Figma 목적지 / 디자인 시스템) 기반 실행 계약
- 단일 화면 편집 가능 레이어 모드 (wrapper frame + 섹션별 `use_figma` + DS 바인딩 + 스크린샷 검증)
- 여러 화면 픽셀 캡처 배치 모드 (`scripts/capture-url.ts` Playwright 드라이버 + 그리드 정렬)
- 디자인 시스템 발견 절차 (`references/design-system-discovery.md`) — 우선순위·매핑표·확신도
- 입력 계약과 조합별 응답 기준 (`references/input-contract.md`)
- 상황별 응답 템플릿 (`references/response-templates.md`)
- Code Connect 1회 프로브 후 미지원 계정 자동 스킵 규칙
