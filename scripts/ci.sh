#!/bin/bash
# The ci gate. Validates the marketplace and each plugin manifest, then
# checks marketplace.json and every plugin.json agree on the version.
set -euo pipefail

claude plugin validate .
claude plugin validate plugins/ship
python3 "$(dirname "$0")/check-manifest-versions.py"

# shellcheck disable=SC2046
python3 "$(dirname "$0")/../plugins/ship/scripts/check-ascii.py" \
  --files $(git ls-files '*.md' '*.json' '*.sh' '*.py')
