# 이슈와 실행 결과

## 이슈 형식

현재 본문 버전은 `orbit/v2.4`다. 고정된 선택지·용어 설명·리뷰어 의견 대신 실제 문제, 영향, 근거, 다음 행동을 전달한다. 빈 섹션을 채우지 않는다.

제목은 `[view: <VIEW>] <확인된 문제>` 형식으로 50자 이내다. 처방을 먼저 단정하기보다 관찰된 상태를 설명한다. 본문에는 `format_version: orbit/v2.4`와 요청 fingerprint에 일치하는 HTML comment를 넣는다.

````markdown
CI와 로컬이 서로 다른 Node.js 버전으로 빌드합니다. 새 문법을 사용하는 변경이 들어오면 로컬 성공과 CI 실패가 갈릴 수 있습니다.

## 근거와 영향

- `package.json:5`: 로컬 도구가 읽는 Node.js 버전 선언
- `.github/workflows/build.yml:18`: 다른 버전의 CI 런타임 선택

두 경로가 같은 build script를 실행하는 것을 확인했습니다. 운영 배포 환경의 버전은 확인하지 못했습니다.

## 다음 행동

두 버전 선언을 하나의 기준으로 맞출지 결정하고, `.github/workflows/build.yml`의 런타임 선택과 저장소의 버전 선언이 그 기준을 따르게 합니다.

<details>
<summary>판정 근거</summary>

영향 4 · 시급성 3 · 확신 medium · 실행 가능성 3.
공통 빌드 경로의 조건부 실패를 근거로 기본 발행 기준을 통과했습니다.

</details>

`format_version: orbit/v2.4`
<!-- orbit-fingerprint: pipeline:owner/repo:BUILD:f-12345678 -->
````

예시의 파일·점수·조건을 실제 관찰처럼 복사하지 않는다. 현재 조사 SHA의 근거를 쓰고 가능한 경우 해당 revision의 permalink를 함께 준다. 내부 용어 설명은 읽는 사람의 판단에 필요할 때만 짧게 덧붙인다.

결정할 trade-off가 있으면 선택지와 기준을 제시할 수 있다. 재현 결함·보안 노출·데이터 손상의 심각성을 정형적인 보류 메뉴로 약화하지 않는다. 반박이나 추가 검증은 실제 결과와 남은 한계를 설명할 때만 포함한다. 내부 사고 과정이나 형식적인 브레인스토밍 기록을 만들지 않는다.

## 발행 호출

스킬 루트에서 다음과 같이 실행한다. body는 실제 줄바꿈을 보존한 UTF-8 파일로 전달한다.

```bash
python3 scripts/publish_issue.py \
  --repo-url https://github.com/owner/repo \
  --title "[view: BUILD] 로컬과 CI의 런타임 버전이 다릅니다" \
  --body-file /tmp/orbit-issue.md \
  --fingerprint "pipeline:owner/repo:BUILD:f-12345678" \
  --labels automation \
  --dry-run
```

발행 권한이 있고 실제 발행 모드면 `--dry-run`을 제외한다. 같은 repo/view의 동일한 과거 문제로 확인한 경우에만 `--legacy-fingerprint`를 추가한다. 다른 view의 fingerprint는 alias로 전달하지 않는다.

publisher는 현재 ID·검증된 alias가 일치하는 open 이슈를 갱신하고 closed 이슈에는 `skipped_closed`를 반환한다. 기존 본문의 버전이 같아도 내용이 달라졌으면 현재 근거로 갱신한다. 이전 형식은 실제 갱신할 때 v2.4로 작성하며, 형식 변경 때문에 새 이슈를 만들지 않는다.

## 결과 구분

- `created`·`updated`: 성공한 이슈 링크를 제공한다.
- `skipped_closed`: 이미 닫힌 이슈 링크를 별도로 기록한다. 자동 재오픈하지 않는다.
- 다른 view에서 추적 중: 그 이슈를 안내하고 새로 발행하지 않는다.
- `manual_required`: 실제 사유와 title/body/labels/fingerprint/legacy_fingerprints가 보존된 payload 파일을 제공한다. 발행 완료로 세지 않는다.
- 응답 불명·일부 실패: 완료가 확인된 결과와 실패한 항목을 구분한다. 재시도 전에 원격 중복 상태를 다시 확인한다.

분석만 한 경우에는 발행되지 않았음을 분명하게 하고 중요한 finding의 근거와 다음 행동을 제공한다. `--dry-run`은 검증한 payload도 함께 제공한다. 통과 finding이 없으면 억지로 이슈 본문을 만들지 않는다.

## 최종 보고

대상 저장소·revision·선택한 관점, 중요한 결과, 발행 모드와 실제 결과를 먼저 설명한다. 조사 누락이나 불확실성이 판단을 제한하면 함께 밝힌다. 작은 실행에 날짜·요일·리뷰어별 통계·내일 관점의 고정 표를 만들지 않는다.

자동화나 상세 보고 요청에서는 관찰 수, 병합 후 finding 수, triage 통과·스킵, created·updated·closed·실패를 수치로 보완할 수 있다. 이 통계는 실제 기록에서 계산하며 서로 다른 상태를 합쳐 성공 수로 부르지 않는다.
