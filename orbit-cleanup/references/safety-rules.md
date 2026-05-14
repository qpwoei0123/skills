# Safety Rules

모든 close 후보는 아래 AND gate를 통과해야 한다.

## Close Gate

1. 마지막 사람 comment가 14일 이내이면 close하지 않고 `cleanup:held-recent-activity`를 붙인다.
2. `orbit:do-not-close`, `orbit:keep`, `pinned` 라벨이 있으면 close하지 않고 `cleanup:held-do-not-close`를 붙인다.
3. `cleanup-log.json`의 `auto_close_runs`가 3 미만이면 close하지 않고 `cleanup:held-trust-ramp`를 붙인다.
4. dry-run이면 모든 원격 mutation을 막는다.
5. 1회 실행당 close 상한은 `MAX_CLOSE_PER_RUN = 10`이다.

## 사람 개입 우선

사람이 reopen한 이슈는 다음 실행에서 close 금지 후보로 기록해야 한다. 자동화가 사람의 최신 판단을 덮어쓰지 않는 것이 원칙이다.

## 실패 처리

원격 API mutation 중 오류가 나면 해당 action만 실패로 기록하고 나머지 action은 계속 시도한다.
마지막 summary의 `errors`에 실패 수를 남긴다.
