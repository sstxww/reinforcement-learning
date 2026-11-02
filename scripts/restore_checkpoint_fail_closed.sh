#!/usr/bin/env bash
# Production training must never treat an expired or failed Artifact as a new model.
set -euo pipefail

: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"
FRESH_START="${FRESH_START:-false}"
if [[ "$FRESH_START" != true && "$FRESH_START" != false ]]; then
  echo "fresh_start must be true or false" >&2
  exit 2
fi
if [[ "$FRESH_START" == true ]]; then
  if [[ "${GITHUB_EVENT_NAME:-}" != workflow_dispatch ]]; then
    echo "Only an explicit manual dispatch may start from scratch" >&2
    exit 2
  fi
  echo "Explicit manual fresh start requested; this is not checkpoint continuation"
  exit 0
fi

mkdir -p checkpoints
if ! RUN_ID="$(gh api "repos/${GITHUB_REPOSITORY}/actions/workflows/train.yml/runs?branch=main&status=success&per_page=1" --jq '.workflow_runs[0].id // empty')"; then
  echo "Cannot query the previous successful training run: refusing random reset" >&2
  exit 3
fi
if [[ -z "$RUN_ID" ]]; then
  echo "No previous successful training run: refusing random reset" >&2
  exit 3
fi
if ! gh run download "$RUN_ID" --repo "$GITHUB_REPOSITORY" --name v1-model --dir checkpoints; then
  echo "Cannot restore Artifact from run $RUN_ID: refusing random reset" >&2
  exit 3
fi
if [[ ! -s checkpoints/model.zip || ! -s checkpoints/model.metadata.json ]]; then
  echo "Partial/empty checkpoint: refusing random reset" >&2
  exit 3
fi
echo "Restored candidate checkpoint from run $RUN_ID; model load and engine checks follow"
