# mr

`version: 0.6.0`

현재 브랜치의 커밋과 diff를 읽고 GitHub PR 또는 GitLab MR을 항상 draft로 계획하거나 생성하는 스킬입니다.

## Quick Start

```text
/mr
/mr --go
/mr -go
```

- `/mr`: draft MR/PR 계획을 제안한 뒤 승인을 기다립니다.
- `/mr --go`, `/mr -go`: 승인 없이 push 후 draft MR/PR을 생성합니다.

두 모드 모두 push 전에 아래를 수행합니다.

- 최근 머지된 MR/PR의 브랜치명으로 레포 컨벤션을 점검하고, 현재 브랜치명이 벗어나면 rename을 제안합니다.
- 커밋 안 된 변경이 남아 있으면 중단하는 대신 commit 스킬을 불러 diff 제외(A안)와 커밋 포함(B안) 두 계획을 나란히 제시하고 선택을 받습니다.

## Structure

```text
mr/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── evals/
│   └── trigger-eval.json
└── scripts/
    └── preflight.sh
```

## Scripts

- `scripts/preflight.sh`: mr 계획에 필요한 읽기 전용 git 사전 점검(worktree 상태, 브랜치/remote, base 후보, 최근 머지 브랜치명 후보, 플랫폼 추정)을 한 번에 출력한다. 아무것도 변경하지 않는다.

```bash
# 스킬 디렉터리에서 실행
bash mr/scripts/preflight.sh
```

## Test

```bash
# 레포 루트에서 실행
python3 scripts/validate_skills.py --skill mr
```
