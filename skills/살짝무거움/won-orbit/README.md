# won-orbit 🪐

`version: 3.0.0`

스킬 목록에서 `won-`으로 찾을 수 있습니다. 명시 호출도 새 이름을 사용합니다.

레포를 관점별로 점검하고, 요청받은 기술 이슈의 생성·갱신까지 수행합니다. 조사 인원과 절차는 실제 범위에 맞춥니다.

## Quick Start

```text
$won-orbit .
$won-orbit . --view BUILD --dry-run
$won-orbit https://github.com/owner/repo --view SAFE --publish
$won-orbit 이 레포의 데이터 흐름을 점검하고 통과한 문제를 이슈로 올려줘.
```

관점이나 주제를 지정하면 우선합니다. 범위가 없는 정기 실행은 월 SAFE, 화 ARCH, 수 DEP, 목 BUILD, 금 DATA, 토 OPS, 일 DOC를 기본으로 합니다. 전체 관점을 요청하면 일곱 관점을 다룹니다.

발행에는 Python 3.10+와 대상 저장소 접근·이슈 쓰기 권한이 필요합니다. 저장소 접근은 이미 인증된 `gh`·`glab` 또는 HTTPS를 우선하고, publisher는 `GITHUB_TOKEN`·`GITLAB_TOKEN` 또는 `~/.orbit/auth.json`을 사용합니다. 인증 파일을 쓸 경우 `github_token`, `gitlab_token`, 선택적 `gitlab_base_url` 키를 설정합니다. 비밀 값은 저장소나 대화에 넣지 않습니다.

## 2.0 전환

기본 `$won-orbit <repo>`는 분석 결과를 제공합니다. 발행을 원하는 자동화에는 `--publish`나 `통과한 문제를 이슈로 발행`을 명시합니다. 이미 같은 작업에서 발행을 허용한 지시는 유지되며, `--dry-run`·`분석만`은 실제 발행을 하지 않습니다. Codex UI의 기본 프롬프트는 발행 요청을 명시하므로 발행까지 수행합니다.

고정 3인 리뷰·교차 반박 라운드·형식적인 선택지 메뉴를 제거했습니다. 필요한 근거 검증과 중복·closed·suppressed 처리는 유지합니다. 이슈 본문은 `orbit/v2.4`로 간결해졌으며 기존 ID와 publisher 계약은 유지합니다.

분석·dry-run은 지속 메모리를 변경하지 않습니다. 발행 실행은 실제 조사 SHA와 원격 결과를 기록하고 실패 후보를 다음 실행에 재확인할 수 있게 남깁니다. 기존 메모리 필드는 읽을 수 있으며 `pending_findings` 등 추가 필드는 필요할 때 기록합니다. 코드 변경만으로 닫힌 이슈를 다시 열지 않습니다.

## Structure

```text
won-orbit/
├── SKILL.md, README.md, CHANGELOG.md, INDEX.md, LICENSE
├── agents/             # 관점별 조사 기준·조정 지침·UI 메타데이터
├── references/         # 근거·선별·메모리·본문 계약
├── evals/              # 기존 트리거·동작 평가 시나리오
└── scripts/            # 순수 계약 함수·publisher·기존 회귀 테스트
```

상세 리소스는 [INDEX.md](INDEX.md)를 참고합니다.

## Scripts

스킬 루트에서 publisher를 직접 실행할 수 있습니다. 이 CLI는 `--dry-run`을 빼면 실제 발행하므로 미리보기에는 아래 옵션을 유지합니다.

```bash
python3 scripts/publish_issue.py \
  --repo-url https://github.com/owner/repo \
  --title "[view: BUILD] 로컬과 CI의 런타임 버전이 다릅니다" \
  --body-file /tmp/orbit-issue.md \
  --fingerprint "pipeline:owner/repo:BUILD:f-12345678" \
  --labels automation \
  --dry-run
```

본문·footer 규칙은 [본문 계약](references/output-templates.md)을 따릅니다. 동일 repo/view의 검증된 과거 ID에만 `--legacy-fingerprint`를 사용합니다. publisher는 pagination·중복 조회·open 갱신·closed 재오픈 방지를 처리하고, 인증·API 실패는 수동 payload로 반환합니다. 이슈가 많은 저장소의 전체 중복 조회는 시간이 걸릴 수 있습니다.

## Test

저장소 루트에서 실행합니다. 새 이슈 발행이나 대상 저장소 코드 실행 없이 기존 회귀 테스트를 확인합니다.

```bash
python3 scripts/validate_skills.py --skill won-orbit
python3 -m unittest discover -s skills/살짝무거움/won-orbit/scripts -p 'test_*.py'
```
