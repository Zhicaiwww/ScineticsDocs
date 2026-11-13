#!/usr/bin/env bash
set -euo pipefail
REPO=/nas/nas8/users/wzc/code/scinetics
BASE=35f9646fb5ca3fd95ca47e862b124bc940c97117
echo "BASE $BASE"
git -C "$REPO" worktree list --porcelain
echo '--- branches ahead of base ---'
while read -r b; do
  n=$(git -C "$REPO" rev-list --count "$BASE..$b")
  if [ "$n" -gt 0 ]; then echo "$n $b"; fi
done < <(git -C "$REPO" for-each-ref --format='%(refname:short)' refs/heads refs/remotes | sort -u)
echo '--- file-level comparison for named branches ---'
for b in codex/fp8-perf-node16-20261025 codex/fp8-merge-gates-20261024 codex/v22-successor-node3 codex/cpt-2b-tps-20261017 codex/pt-stability-20261019 codex/v23-resume-24gpu-20261025 feat/tool-sft-runtime-20261028 codex/spike-diagnosis-v20 codex/token-loss-safety codex/packmix-v22; do
  printf '%s\t' "$b"
  git -C "$REPO" diff --stat "$BASE...$b" | tail -n 1
done
