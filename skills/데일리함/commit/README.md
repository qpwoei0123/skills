# commit

`version: 0.6.1`

현재 git 변경사항을 읽고 레포 커밋 규칙과 최근 커밋 로그 스타일에 맞춰 Conventional Commits 형식의 한글 커밋을 계획하거나 실행하는 스킬입니다.

## Quick Start

```text
/commit
/commit --go
/commit -go
```

- `/commit`: diff를 분석하고 커밋 계획을 제안한 뒤 승인을 기다립니다.
- `/commit --go`, `/commit -go`: 승인 없이 바로 적절한 단위로 커밋합니다.

메시지를 정하기 전에 레포 기여 문서(CONTRIBUTING, commitlint 설정 등)를 먼저 확인하고, 커밋 규칙이 있으면 최근 로그 스타일보다 우선 적용합니다.

## Structure

```text
commit/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── agents/
│   └── openai.yaml
├── evals/
│   └── trigger-eval.json
└── scripts/
    └── collect_context.sh
```

## Scripts

- `scripts/collect_context.sh`: 커밋 계획에 필요한 읽기 전용 개요(브랜치 포함 status, 최근 로그, unstaged/staged diff --stat, untracked 목록, 기여 문서·커밋 규칙 후보)를 한 번에 출력합니다. 아무것도 변경하지 않으며, 현재 git 작업 트리가 아니면 오류로 중단합니다.

커밋할 대상 레포 안에서 스킬 디렉터리 경로로 실행:

```bash
bash <스킬 디렉터리>/scripts/collect_context.sh
```

## Test

레포 루트에서 실행:

```bash
python3 scripts/validate_skills.py --skill commit
```
