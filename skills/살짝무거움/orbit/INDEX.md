# orbit 리소스

기본 실행은 [SKILL.md](SKILL.md)와 선택한 view의 조사 기준에서 시작한다. 아래 자료는 필요한 경우에만 읽는다.

| 리소스 | 용도 |
|---|---|
| [README.md](README.md) | 사용·인증·테스트와 2.0 전환 |
| [agents/orchestrator.md](agents/orchestrator.md) | 분담 조사와 결과 조정 |
| [SAFE](agents/SAFE.md), [ARCH](agents/ARCH.md), [DEP](agents/DEP.md), [BUILD](agents/BUILD.md), [DATA](agents/DATA.md), [OPS](agents/OPS.md), [DOC](agents/DOC.md) | 관점별 조사 범위와 반례 |
| [공통 조사 기준](references/agent-playbook.md) | 근거·영향 경로·설정 실제값 확인 |
| [저장소 유형](references/repo-types.md) | 실제 아키텍처에 맞는 적용 |
| [결과 계약](references/execution-lifecycle.md) | 채점, observation과 result JSON |
| [발행 기준 조정](references/triage-rules.md) | 명시적 override와 상태 처리 |
| [조사 메모리](references/coverage-log-schema.md) | revision·범위·pending·원격 상태 기록 |
| [본문과 결과](references/output-templates.md) | orbit/v2.4 이슈 본문과 발행 결과 |
| [pipeline_contracts.py](scripts/pipeline_contracts.py) | 기본 view·채점·triage·ID 함수 |
| [publish_issue.py](scripts/publish_issue.py) | fingerprint·alias 중복 처리와 create/update |

기존 테스트는 스킬 루트에서 실행한다.

```bash
python3 -m unittest discover -s scripts -p 'test_*.py'
```

변경 이력은 [CHANGELOG.md](CHANGELOG.md)에 있다.
