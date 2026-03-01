#!/usr/bin/env bash
set -euo pipefail

# 一键答辩校验（Linux/Mac）
# 用法：bash tools/run_defense_demo_check.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

python tools/run_defense_demo_check.py
