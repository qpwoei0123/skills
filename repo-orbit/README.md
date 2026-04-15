```text
  ════════════════════════════════════════════════════════╗
║  ____  _____ ____   ___    ══════════     ══════════  ═ ║
║ |  _ \| ____|  _ \ / _ \      ═══════════ ══  ═════ ═══ ║
║ | |_) |  _| | |_) | | | |  ___  ____  ____ ___ _____    ║
║ |  _ <| |___|  __/| |_| | / _ \|  _ \| __ )_ _|_   _|  ═║
║ |_| \_\_____|_|    \___/ | | | | |_) |  _ \| |  | |     ║
║  ══════════   ══  ═════  | |_| |  _ <| |_) | |  | | ═══ ║
║═══  ═══════════   ═══     \___/|_| \_\____/___| |_|   ══║
╚══════════════════════════════════════════════════════════
```

# repo orbit 🪐

`version: 1.7.0`

요일별 고정 view로 레포를 분석하고, triage를 통과한 finding만 이슈로 발행하는 스킬입니다.

## 포함 파일

```text
repo-orbit/                          # 스킬 루트
├── SKILL.md                         # 스킬 메인 규칙과 실행 흐름
├── assets/                          # README용 시각 에셋
│   └── repo-orbit.png               # repo-orbit 대표 이미지
├── agents/                          # view별 에이전트와 Orchestrator 지침
│   ├── orchestrator.md              # 공통 제어, 병합, triage, 발행 규칙
│   ├── SAFE.md                      # 변경 안전성 view 지침
│   ├── ARCH.md                      # 경계 건강도 view 지침
│   ├── DEP.md                       # 의존성/설정 안정성 view 지침
│   ├── BUILD.md                     # 빌드/배포 재현성 view 지침
│   ├── DATA.md                      # 데이터 구조 & 흐름 view 지침
│   ├── OPS.md                       # 운영 관측성 view 지침
│   └── DOC.md                       # 지식 내구성 view 지침
├── references/                      # 공통 참조 문서와 출력 계약
│   ├── agent-playbook.md            # 에이전트 공통 조사 원칙과 승격 조건
│   ├── execution-lifecycle.md       # Step 3~4.5 실행 세부 규칙
│   ├── triage-rules.md              # triage override와 재검토 기준
│   ├── output-templates.md          # 이슈 본문과 최종 보고 템플릿
│   ├── coverage-log-schema.md       # coverage-log/result 저장 스키마
│   └── view-playbooks.md            # 과거 플레이북 호환 안내
└── scripts/                         # 자동 발행과 테스트 스크립트
    ├── publish_issue.py             # GitHub/GitLab 이슈 create/update (closed 이슈는 재오픈하지 않음)
    └── test_publish_issue.py        # 발행 스크립트 회귀 테스트
```

## 요구사항

- Python 3.10+
- Git 접근 권한
- 이슈를 올릴 대상 레포 URL

자동 발행을 쓰려면 아래 둘 중 하나가 필요합니다.

- `GITHUB_TOKEN` 또는 `GITLAB_TOKEN`
- `~/.repo-orbit/auth.json`

## auth.json 예시

```json
{
  "github_token": "ghp_xxx",
  "gitlab_token": "glpat-xxx",
  "gitlab_base_url": "https://gitlab.example.com"
}
```

## 사용 예시

```text
# 기본 실행
$repo-orbit https://github.com/owner/repo

# 특정 view 강제 지정
$repo-orbit https://github.com/owner/repo --view SAFE

# 분석만 하고 이슈 발행은 건너뜀
$repo-orbit https://github.com/owner/repo --dry-run
```

발행 스크립트를 직접 실행할 때:

```bash
python3 scripts/publish_issue.py \
  --repo-url https://github.com/owner/repo \
  --title "[view: BUILD] 로컬과 CI 빌드 경로가 다릅니다" \
  --body-file /tmp/repo-orbit-issue.md \
  --fingerprint "pipeline:owner/repo:BUILD:E1" \
  --labels automation

# dry-run (API 호출 없이 payload만 출력)
python3 scripts/publish_issue.py \
  --repo-url https://github.com/owner/repo \
  --title "[view: BUILD] ..." \
  --body-file /tmp/repo-orbit-issue.md \
  --fingerprint "pipeline:owner/repo:BUILD:E1" \
  --labels automation \
  --dry-run
```

## 자동 발행 실패 시 동작

아래 상황에서는 API 호출을 포기하고, 수동 복붙용 출력만 JSON으로 반환합니다.

- 인증 토큰이 없을 때
- GitHub / GitLab API 네트워크 호출이 실패할 때

이때 출력에는 아래 정보가 포함됩니다.

- `title`
- `body`
- `labels`
- `fingerprint`
- `copy_paste_text`

## 알려진 제한

- fingerprint 중복 검색은 GitHub/GitLab API를 페이지네이션으로 전체 순회합니다. 이슈가 매우 많은 레포(수천 개 이상)에서는 첫 실행 시 시간이 걸릴 수 있습니다.
- 라벨 생성 권한이 없는 환경에서는 자동 발행이 수동 복붙 출력으로 내려갈 수 있습니다.
- shallow clone(기본값)으로 접근한 레포에서 히스토리가 필요한 분석은 일부 제한될 수 있습니다.

## 테스트

```bash
python3 scripts/test_publish_issue.py
```
