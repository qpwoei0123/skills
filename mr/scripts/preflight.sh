#!/usr/bin/env bash
# mr 계획에 필요한 읽기 전용 git 사전 점검을 한 번에 출력한다. 아무것도 변경하지 않는다.
set -uo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "[error] 현재 위치가 git 작업 트리가 아닙니다." >&2
  exit 1
fi

branch=$(git branch --show-current)

echo "# worktree status (출력이 있으면 dirty)"
git status --short
echo
echo "# branch / remote"
echo "current: $branch"
git remote -v | sed -n '1,2p'
echo
echo "# base 후보 (위에서부터 우선)"
git config "branch.$branch.gh-merge-base" 2>/dev/null || true
git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@refs/remotes/origin/@@' || true
echo
echo "# 플랫폼 추정"
url=$(git remote get-url origin 2>/dev/null || true)
case "$url" in
  *github.com*) echo "GitHub" ;;
  *[Gg]it[Ll]ab*) echo "GitLab" ;;
  "") echo "판단 불가: origin remote 없음" ;;
  *) echo "판단 불가: $url" ;;
esac
