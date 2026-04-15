# skills

개인 에이전트 스킬 저장소입니다.

## Install

```bash
npx skills add qpwoei0123/skills
```

## Standard

- [docs/SKILL-STANDARD.md](/Users/han-won-yeong/Documents/project/skills/docs/SKILL-STANDARD.md): 이 저장소의 스킬 최소 형식과 편입 규칙

## Structure

```text
skills/
├── docs/
│   └── SKILL-STANDARD.md           # 저장소 공통 스킬 최소 형식
├── scripts/
│   └── validate_skills.py          # accepted 스킬 형식 검증 스크립트
├── .github/
│   └── workflows/
│       └── validate-skills.yml     # 스킬 형식 자동 검증 CI
├── orbit/                      # 레포 점검/이슈 발행 워크플로 스킬
│   ├── SKILL.md                     # 스킬 메인 규칙과 실행 흐름
│   ├── assets/                      # README용 시각 에셋
│   │   └── orbit.png           # orbit 대표 이미지
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
├── ghostwriter/                     # 사용자 문체 기반 글쓰기 스킬
│   ├── SKILL.md                     # 스킬 메인 규칙과 작성 플로우
│   ├── README.md                    # 빠른 시작과 검증 방법
│   ├── CHANGELOG.md                 # 변경 이력
│   └── references/
│       └── profile-template.md      # 글쓴이 프로필 템플릿
```

## Included Skills

- `orbit 🪐` : 레포를 요일별 관점으로 분석하고 finding을 이슈로 발행하는 실험적 워크플로 스킬
- `ghostwriter`: 사용자 문체를 분석해 그 사람처럼 글을 써주는 글쓰기 스킬
