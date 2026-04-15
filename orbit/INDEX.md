# orbit 문서 인덱스

처음 이 스킬을 접하는 경우 아래 순서로 읽는다.

## 빠른 시작

1. **[SKILL.md](SKILL.md)** — 파이프라인 전체 흐름 (Step 1~6), triage 기준, 발행 규칙
2. **[README.md](README.md)** — 설치 요건, 인증 설정, Quick Start 예시

## 에이전트 지침

| 파일 | 역할 |
|------|------|
| [agents/orchestrator.md](agents/orchestrator.md) | 병합·채점·발행 공통 제어 |
| [agents/SAFE.md](agents/SAFE.md) | 변경 안전성 (월) |
| [agents/ARCH.md](agents/ARCH.md) | 경계 건강도 (화) |
| [agents/DEP.md](agents/DEP.md) | 의존성/설정 안정성 (수) |
| [agents/BUILD.md](agents/BUILD.md) | 빌드/배포 재현성 (목) |
| [agents/DATA.md](agents/DATA.md) | 데이터 구조 & 흐름 (금) |
| [agents/OPS.md](agents/OPS.md) | 운영 관측성 (토) |
| [agents/DOC.md](agents/DOC.md) | 지식 내구성 (일) |

## 참조 문서

| 파일 | 언제 읽나 |
|------|-----------|
| [references/execution-lifecycle.md](references/execution-lifecycle.md) | observation/rebuttal/query JSON 형식, timeout SLA |
| [references/output-templates.md](references/output-templates.md) | 이슈 본문 템플릿, v2 포맷, 이의 제기 렌더링 |
| [references/triage-rules.md](references/triage-rules.md) | override 옵션, 기준 재검토 트리거 |
| [references/repo-types.md](references/repo-types.md) | 레포 유형 판정, FSD/백엔드/모노레포별 view 적용 |
| [references/agent-playbook.md](references/agent-playbook.md) | 에이전트 공통 조사 원칙, finding 승격 조건 |
| [references/coverage-log-schema.md](references/coverage-log-schema.md) | per-view 메모리 스키마, 탐색 나침반, 실행 이력 |

## 스크립트

| 파일 | 역할 |
|------|------|
| [scripts/publish_issue.py](scripts/publish_issue.py) | GitHub/GitLab 이슈 create/update, fingerprint 중복 체크 |
| [scripts/test_publish_issue.py](scripts/test_publish_issue.py) | publish_issue.py 회귀 테스트 |
| [scripts/test_pipeline.py](scripts/test_pipeline.py) | Step 1~5 파이프라인 로직 단위 테스트 |

## 테스트 실행

```bash
# 발행 스크립트 테스트
python3 -m unittest scripts/test_publish_issue.py -v

# 파이프라인 로직 테스트
python3 -m unittest scripts/test_pipeline.py -v
```

## 버전 히스토리

[CHANGELOG.md](CHANGELOG.md) 참조.

## 핵심 정책 요약

- **closed 이슈**: 재오픈하지 않는다. `skipped_closed`로 기록.
- **triage**: impact≥4, urgency≥3, confidence≠low, actionability≥3 모두 충족해야 발행.
- **에이전트**: 사실 관찰만 반환. 점수는 Orchestrator만 부여.
- **format_version**: 이슈 본문 포맷이 바뀔 때만 올린다. 현재: `orbit/v2.1`
