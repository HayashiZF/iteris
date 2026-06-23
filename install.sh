#!/bin/bash
set -euo pipefail

# Default repository and branch settings
REPO_URL="https://github.com/HayashiZF/iteris.git"
BRANCH="plugin-codex"

# If run inside a git repository, dynamically detect the remote and branch/commit
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || true)
  if [ -n "$CURRENT_REMOTE" ]; then
    REPO_URL="$CURRENT_REMOTE"
  fi
  CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || true)
  if [ -n "$CURRENT_BRANCH" ]; then
    BRANCH="$CURRENT_BRANCH"
  fi
fi

# Check if git command is available
if ! command -v git >/dev/null 2>&1; then
  echo "Error: git is not installed or not in PATH." >&2
  exit 1
fi

# Parse parameters
GLOBAL_MODE=0
for arg in "$@"; do
  if [ "$arg" = "-global" ] || [ "$arg" = "--global" ]; then
    GLOBAL_MODE=1
  fi
done

# Create a temporary directory for cloning
TEMP_DIR="./.iteris_temp_$(date +%Y%m%d%H%M%S)_$$"
mkdir -p "$TEMP_DIR"

# Ensure cleanup of the temporary directory on exit or failure
cleanup() {
  if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
  fi
}
trap cleanup EXIT INT TERM

echo "Starting installation..."
echo "Source Repository: $REPO_URL"
echo "Source Branch/Ref: $BRANCH"

# Clone the specified branch with depth 1
if ! git clone --depth 1 --branch "$BRANCH" --single-branch "$REPO_URL" "$TEMP_DIR" >/dev/null 2>&1; then
  echo "Warning: Failed to clone branch '$BRANCH'. Attempting default branch..."
  if ! git clone --depth 1 "$REPO_URL" "$TEMP_DIR" >/dev/null 2>&1; then
    echo "Error: Failed to clone repository $REPO_URL." >&2
    exit 1
  fi
fi

# 1. Download plugins/ to current directory
if [ -d "$TEMP_DIR/plugins" ]; then
  echo "Installing plugins/ to the current directory..."
  mkdir -p plugins
  cp -r "$TEMP_DIR/plugins/." plugins/
else
  echo "Warning: 'plugins' directory not found in repository."
fi

# 2. Download .agents/ to current directory
if [ -d "$TEMP_DIR/.agents" ]; then
  echo "Installing .agents/ to the current directory..."
  mkdir -p .agents
  cp -r "$TEMP_DIR/.agents/." .agents/
else
  echo "Warning: '.agents' directory not found in repository."
fi

# 3. Handle .codex/ directory destination based on -global param
TARGET_CODEX_DIR=".codex"
if [ "$GLOBAL_MODE" -eq 1 ]; then
  TARGET_CODEX_DIR="$HOME/.codex"
fi

if [ -d "$TEMP_DIR/.codex" ]; then
  if [ -d "$TARGET_CODEX_DIR" ]; then
    echo "Merging .codex/ into existing destination: $TARGET_CODEX_DIR"
  else
    echo "Installing .codex/ to: $TARGET_CODEX_DIR"
  fi
  mkdir -p "$TARGET_CODEX_DIR"
  cp -r "$TEMP_DIR/.codex/." "$TARGET_CODEX_DIR/"
else
  echo "Warning: '.codex' directory not found in repository."
fi

echo "Installation complete!"
