#!/bin/sh
set -eu
RESUME_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ -n "${RESUME_PYTHON:-}" ]; then
    RESUME_RUNTIME="$RESUME_PYTHON"
elif [ -x "$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3" ]; then
    RESUME_RUNTIME="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
elif [ -x "$RESUME_ROOT/.venv/bin/python3" ]; then
    RESUME_RUNTIME="$RESUME_ROOT/.venv/bin/python3"
else
    RESUME_RUNTIME=python3
fi
exec "$RESUME_RUNTIME" "$RESUME_ROOT/build.py" "$@"
