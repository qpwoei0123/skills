# repo-orbit

요일별 고정 view로 레포를 분석하고, triage를 통과한 finding만 이슈로 발행하는 스킬입니다.

## 포함 파일

```text
repo-orbit/
├── SKILL.md
├── agents/
├── references/
└── scripts/
```

## 요구사항

- Python 3
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
$repo-orbit
$repo-orbit --summary
$repo-orbit --focus-view BUILD
```

발행 스크립트를 직접 실행할 때:

```bash
python3 scripts/publish_issue.py \
  --repo-url https://github.com/owner/repo \
  --title "[view: BUILD] 로컬과 CI 빌드 경로가 다릅니다" \
  --body-file /tmp/repo-orbit-issue.md \
  --fingerprint "pipeline:owner/repo:BUILD:E1" \
  --labels automation
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

- fingerprint 중복 검색은 최근 이슈 100개만 확인합니다.
- 오래된 이슈가 100개 범위 밖으로 밀리면 중복 update 대신 새 이슈가 생길 수 있습니다.
- 라벨 생성 권한이 없는 환경에서는 자동 발행이 수동 복붙 출력으로 내려갈 수 있습니다.

## 테스트

```bash
python3 scripts/test_publish_issue.py
```
