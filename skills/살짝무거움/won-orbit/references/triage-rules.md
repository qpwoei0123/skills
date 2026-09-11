# 발행 기준과 조정

기본 기준은 impact ≥ 4, urgency ≥ 3, confidence ≠ low, actionability ≥ 3이다. 근거와 영향 경로가 성립한 finding에 적용한다. 기본 계산은 `scripts/pipeline_contracts.py`를 사용한다.

## 명시적 override

| 옵션 | 기본값 |
|---|---:|
| `--triage-min-impact` | 4 |
| `--triage-min-urgency` | 3 |
| `--triage-min-score` | 3 |
| `--triage-allow-low-confidence` | false |

사용자가 명시한 값을 적용하고 실행 기록에 실제 기준과 `triage_override: true`를 남긴다. 기본 helper의 `triage_pass`는 override 인자를 받지 않으므로 이 경우 동일한 비교 순서에 지정된 기준을 적용한다. 점수 범위 1~5 밖의 값 등 잘못된 입력은 임의로 보정하지 않는다.

`--triage-allow-low-confidence`가 있어도 근거 없는 주장을 만들 수는 없다. 확인된 사실과 남은 조건을 명확히 나누며, 반례로 철회된 claim은 발행하지 않는다. 이 옵션만으로 발행 권한이 생기지는 않는다.

## 기준을 다시 볼 때

실제 오탐, 중복, 누락 사례가 기준과 연결될 때 조정을 제안한다. 발행 0건이 반복되거나 이슈가 많다는 사실만으로 기준을 낮추거나 올리지 않는다. 같은 view·비슷한 조사 범위의 실행을 비교하고 사용자가 수용한 기준을 유지한다.

`low_actionability`가 많으면 실제 다음 행동이 모호한지, 문자열 heuristic 때문에 낮게 계산됐는지 구분한다. 점수에 맞추기 위한 문장 꾸미기를 하지 않는다.

## 상태와 재발행

open 상태의 동일 문제는 triage를 통과하면 갱신할 수 있다. 형식 버전이 같아도 실제 근거·claim·next_step이 달라졌으면 본문을 갱신한다.

closed는 자동 재오픈하거나 새 ID로 대체 발행하지 않는다. suppressed도 자동 해제하지 않는다. 다른 view의 동일 문제는 해당 view의 기존 이슈를 가리킨다. 메모리와 원격 상태가 다르면 확인된 원격 결과를 기록한다.

통과 후보가 0개여도 정상 결과다. 분석 결과와 발행 결과를 구분하고, 중요한 미확정은 발행된 finding으로 포장하지 않는다.
