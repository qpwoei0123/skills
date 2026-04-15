# skills

개인 에이전트 스킬 저장소입니다.

## Install

```bash
npx skills add qpwoei0123/skills
```

## Structure

```text
skills/
├── repo-orbit/                      # 레포 점검/이슈 발행 워크플로 스킬
│   ├── SKILL.md                     # 스킬 메인 규칙과 실행 흐름
│   ├── assets/                      # README용 시각 에셋
│   │   └── repo-orbit.png           # repo-orbit 대표 이미지
│   ├── agents/                      # view별 에이전트와 Orchestrator 지침
│   │   ├── orchestrator.md          # 공통 제어, 병합, triage, 발행 규칙
│   │   ├── SAFE.md                  # 변경 안전성 view 지침
│   │   ├── ARCH.md                  # 경계 건강도 view 지침
│   │   ├── DEP.md                   # 의존성/설정 안정성 view 지침
│   │   ├── BUILD.md                 # 빌드/배포 재현성 view 지침
│   │   ├── DATA.md                  # 데이터 구조 & 흐름 view 지침
│   │   ├── OPS.md                   # 운영 관측성 view 지침
│   │   └── DOC.md                   # 지식 내구성 view 지침
│   ├── references/                  # 공통 참조 문서와 출력 계약
│   │   ├── agent-playbook.md        # 에이전트 공통 조사 원칙과 승격 조건
│   │   ├── execution-lifecycle.md   # Step 3~4.5 실행 세부 규칙
│   │   ├── triage-rules.md          # triage override와 재검토 기준
│   │   ├── output-templates.md      # 이슈 본문과 최종 보고 템플릿
│   │   ├── coverage-log-schema.md   # coverage-log/result 저장 스키마
│   │   └── view-playbooks.md        # 과거 플레이북 호환 안내
│   └── scripts/                     # 자동 발행과 테스트 스크립트
│       ├── publish_issue.py         # GitHub/GitLab 이슈 create/update/reopen
│       └── test_publish_issue.py    # 발행 스크립트 회귀 테스트
└── welcome/                         # 최소 SKILL.md 예시 스킬
    └── SKILL.md                     # 기본 템플릿
```

## Included Skills

- `repo-orbit 🪐` : 레포를 요일별 관점으로 분석하고 finding을 이슈로 발행하는 실험적 워크플로 스킬
- `welcome`: 최소 `SKILL.md` 구조 예시
