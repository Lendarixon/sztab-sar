#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 tools/setup_sztab.py "$@"
python3 app.py
