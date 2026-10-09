#!/bin/bash
# The ci gate. Validates the marketplace and every plugin manifest, then
# checks marketplace.json carries no version and every plugin.json has one.
set -euo pipefail

claude plugin validate .
for plugin_dir in plugins/*/; do
  claude plugin validate "${plugin_dir%/}"
done
python3 "$(dirname "$0")/check-manifest-versions.py"
