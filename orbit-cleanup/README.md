# orbit-cleanup

`version: 1.0.0`

orbit가 이미 발행한 GitHub/GitLab 이슈를 주기적으로 정리하는 큐레이션 스킬입니다.
중복, 일괄 처리 후보, 이미 해결된 이슈를 분류하고 라벨, 정형 comment, 조건부 close, orbit 메모리 갱신을 자동화합니다.

## Quick Start

```text
$orbit-cleanup https://github.com/owner/repo
$orbit-cleanup https://github.com/owner/repo --dry-run
```

스크립트를 직접 실행할 때:

```bash
python3 orbit-cleanup/scripts/cleanup_issue.py \
  --repo-url https://github.com/owner/repo \
  --dry-run
```

오프라인 dry-run:

```bash
python3 orbit-cleanup/scripts/cleanup_issue.py \
  --repo-url https://github.com/owner/repo \
  --issues-file /tmp/orbit-issues.json \
  --dry-run
```

## Structure

```text
orbit-cleanup/
├── SKILL.md
├── INDEX.md
├── README.md
├── CHANGELOG.md
├── agents/
│   ├── orchestrator.md
│   ├── DUP.md
│   ├── BATCH.md
│   └── RESOLVED.md
├── references/
│   ├── classification-rules.md
│   ├── action-matrix.md
│   ├── safety-rules.md
│   ├── comment-templates.md
│   └── memory-schema.md
└── scripts/
    ├── cleanup_issue.py
    ├── classify.py
    ├── memory_bridge.py
    ├── schedule_setup.md
    └── test_cleanup_issue.py
```

## Schedule

schedule 스킬 또는 외부 cron에는 아래 의도를 등록합니다. 스킬은 자동 등록하지 않습니다.

```text
0 3 * * 0
$orbit-cleanup https://github.com/owner/repo
```

기준 시간대는 KST를 권장합니다.

## Test

```bash
python3 -m unittest orbit-cleanup/scripts/test_cleanup_issue.py
python3 scripts/validate_skills.py --skill orbit-cleanup
```

전체 저장소 검증:

```bash
python3 -m unittest discover
python3 scripts/validate_skills.py
```
