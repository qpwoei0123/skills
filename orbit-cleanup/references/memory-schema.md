# Memory Schema

orbit-cleanup은 orbit memory를 직접 갱신해 다음 orbit 실행의 `skipped_closed` 흐름과 맞춘다.

## View memory

경로:

```text
~/.orbit/<owner>/<repo>/<VIEW>.json
```

관련 필드:

```json
{
  "known_findings": {
    "pipeline:owner/repo:DATA:f-11111111": {
      "status": "open"
    }
  }
}
```

## 상태 갱신

- RESOLVED high close: `status = "closed"`
- DUP close: `status = "suppressed"`, `alias_of = "<canonical fingerprint>"`
- BATCH: status 변경 없음, `cleanup_tags`에 `batch:<module>` 추가

## cleanup-log.json

경로:

```text
~/.orbit/<owner>/<repo>/cleanup-log.json
```

스키마:

```json
{
  "last_run_at": "2026-05-14T03:00:00+09:00",
  "auto_close_runs": 0,
  "history": [
    {
      "run_at": "...",
      "scanned": 42,
      "dup": 3,
      "batch": 5,
      "resolved": 2,
      "closed": 0,
      "label_only": 10,
      "errors": 0
    }
  ]
}
```

`auto_close_runs`는 실제 close가 하나 이상 성공한 실행 뒤에만 증가한다.
