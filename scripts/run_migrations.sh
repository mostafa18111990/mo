#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../control-panel"
alembic upgrade head
echo "Migrations complete."
