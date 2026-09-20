#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: $0 /path/to/upstream/DREAMPlace" >&2
  exit 2
fi

UPSTREAM=$1
if [ ! -d "$UPSTREAM/dreamplace" ]; then
  echo "not a DREAMPlace checkout: $UPSTREAM" >&2
  exit 2
fi

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
export PYTHONPATH="$ROOT/src/diffnet_prototype:$UPSTREAM:${PYTHONPATH:-}"
cd "$ROOT"
# The integration-hook test needs the patch applied to the upstream checkout;
# the remaining tests exercise only the collected local prototype modules.
exec python -m pytest -q src/diffnet_prototype/tests -k 'not placeobj_net_moving_hook'
