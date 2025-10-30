#!/usr/bin/env bash
# Create base branches from dev using a temporary clone per branch.
# This avoids touching the main working tree and prevents checkout conflicts.
#
# Usage:
#  ./create_base_branches_v2.sh --dry-run
#  ./create_base_branches_v2.sh --run
# Options:
#  --force       Delete and recreate remote branch if exists
#  -h|--help     Show help

set -euo pipefail

GIT_REMOTE=${GIT_REMOTE:-origin}
DRY_RUN=true
FORCE=false

function usage(){
  cat <<EOF
Usage: $0 [--dry-run|--run] [--force]
Creates base/<CATEGORY>/<PROJECT> branches from dev by cloning the repo
into a temporary directory for each branch so the main working tree is not modified.

Options:
  --dry-run  (default) show actions
  --run      perform actions
  --force    delete remote branch first if it exists
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --run) DRY_RUN=false; shift ;;
    --force) FORCE=true; shift ;;
    -h|--help) usage ;;
    *) echo "Unknown arg: $1"; usage ;;
  esac
done

# Define projects based on the monorepo structure
declare -A PROJECTS
PROJECTS[IOT]="arduino"
PROJECTS[DEEP_LEARNING]="deep-learning-server"
PROJECTS[AI]="llm-gateway mcp-server"
PROJECTS[APP]="web-app web-page"
PROJECTS[SERVER]="app-server iot-data-server local-hub ros2-server vllm-server path-planning-server sim-resource-server"
PROJECTS[ROS2]="pinky_pro rfred"

if ! git show-ref --verify --quiet refs/heads/dev; then
  echo "Branch 'dev' not found locally. Please fetch or create it first." >&2
  exit 1
fi

# fetch to ensure up to date
git fetch --all --prune

for CATEGORY in "${!PROJECTS[@]}"; do
  for PROJECT in ${PROJECTS[$CATEGORY]}; do
    BRANCH="base/${CATEGORY}/${PROJECT}"
    PROJECT_PATH="${CATEGORY}/${PROJECT}"

    echo "---\nProcessing: $BRANCH (path: $PROJECT_PATH)"

    if git ls-remote --heads ${GIT_REMOTE} ${BRANCH} | grep -q .; then
      if [ "$FORCE" = true ]; then
        if $DRY_RUN; then
          echo "(dry-run) would delete remote branch ${GIT_REMOTE}/${BRANCH}"
        else
          git push ${GIT_REMOTE} --delete ${BRANCH} || true
        fi
      else
        echo "Remote branch exists, skipping: ${BRANCH}"
        continue
      fi
    fi

    if $DRY_RUN; then
      echo "(dry-run) would: clone repo to tmp, checkout dev, create branch $BRANCH, keep only $PROJECT_PATH, commit and push"
      continue
    fi

    TMPDIR=$(mktemp -d)
    echo "Cloning into temporary dir: $TMPDIR"
    git clone . "$TMPDIR" >/dev/null 2>&1
    pushd "$TMPDIR" >/dev/null

    # create branch based on dev
    git switch dev
    git switch -c "$BRANCH"

    # remove all from index, then add only project path if present
    # git rm -r --cached . >/dev/null 2>&1 || true
    # if [ -e "$PROJECT_PATH" ]; then
    #   git add -- "$PROJECT_PATH"
    # else
    #   echo "Warning: path does not exist in repo: $PROJECT_PATH"
    # fi

    if git diff --cached --quiet; then
      git commit --allow-empty -m "Init $BRANCH: track only $PROJECT_PATH"
    else
      git commit -m "Init $BRANCH: track only $PROJECT_PATH"
    fi

    echo "Pushing $BRANCH -> ${GIT_REMOTE}"
    git push ${GIT_REMOTE} HEAD:${BRANCH}

    popd >/dev/null
    rm -rf "$TMPDIR"
  done
done

echo "Done."