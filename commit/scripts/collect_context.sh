#!/usr/bin/env bash
# 커밋 계획에 필요한 읽기 전용 개요를 한 번에 출력한다.
# 현재 작업 디렉터리의 git 레포를 대상으로 하며 아무것도 변경하지 않는다.
set -uo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "[error] 현재 위치가 git 작업 트리가 아닙니다." >&2
  exit 1
fi

echo "# status (브랜치 포함)"
git status -sb
echo
echo "# recent log"
git log --oneline -12
echo
echo "# diff --stat (unstaged)"
git diff --stat
echo
echo "# diff --cached --stat (staged)"
git diff --cached --stat
echo
echo "# untracked (최대 50개)"
untracked=$(git ls-files --others --exclude-standard)
echo "$untracked" | head -50
count=$(printf '%s' "$untracked" | grep -c . || true)
if [ "$count" -gt 50 ]; then
  echo "... 외 $((count - 50))개"
fi
