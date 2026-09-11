#!/bin/bash
#
# SessionStart hook for Claude Code on the web. Exits at once elsewhere.
# Cloud sessions read .claude/settings.json but do not install a plugin
# from an external marketplace source, so install ship here.
# See: https://code.claude.com/docs/en/discover-plugins.md
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

if command -v claude >/dev/null 2>&1; then
  claude plugin marketplace add josephdaw/claude-plugins --scope user >/dev/null 2>&1 \
    && echo "session-start: josephdaw marketplace ready" \
    || echo "session-start: marketplace add failed or already present, continuing" >&2
  claude plugin install ship@josephdaw --scope user -y >/dev/null 2>&1 \
    && echo "session-start: ship plugin ready" \
    || echo "session-start: ship plugin install failed or already present, continuing" >&2
else
  echo "session-start: claude CLI not on PATH, skipping ship plugin install" >&2
fi
