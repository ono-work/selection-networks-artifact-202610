#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")/.."
exec python3 -m src.run_v49_d6_tail_partitioned "$@"
