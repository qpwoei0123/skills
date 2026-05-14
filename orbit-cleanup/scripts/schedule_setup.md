# Schedule Setup

orbit-cleanup은 schedule을 자동 등록하지 않는다. 사용자가 의도적으로 등록할 때 아래 형태를 쓴다.

## Weekly KST

```text
0 3 * * 0
$orbit-cleanup https://github.com/owner/repo
```

## Dry-run rehearsal

처음 3회는 safety gate가 close를 막으므로 라벨과 comment 결과를 확인한다.

```text
$orbit-cleanup https://github.com/owner/repo --dry-run
```
