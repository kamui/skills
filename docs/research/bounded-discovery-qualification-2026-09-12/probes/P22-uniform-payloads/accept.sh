#!/bin/sh
# P22: accept every arm's payload under the one contract, then check uniformity over all
# receipts before anything is masked.
set -u
PAY="$1"; FIND="$2"; CLEAN="$3"; OUT="$4"
mkdir -p "$OUT"
status=0
for arm in A B C; do
  for name in findings clean stopped; do
    completion=complete
    work="$FIND/$arm-$name"
    [ "$name" = clean ] && work="$CLEAN/$arm-clean"
    if [ "$name" = stopped ]; then completion=stopped-budget; work="$CLEAN/$arm-stopped"; fi
    echo "== arm $arm $name (completion $completion) =="
    python3 "$PAY" accept --work "$work" --arm "$arm" \
      --attempt "probe-p22-$arm-$name" --completion "$completion" \
      --receipt "$OUT/$arm-$name.receipt.json" 2>&1 | head -4 || status=1
  done
done
echo "== uniformity over every receipt, before masking =="
set -- 
for arm in A B C; do
  for name in findings clean stopped; do
    set -- "$@" --receipt "$OUT/$arm-$name.receipt.json"
  done
done
python3 "$PAY" uniformity "$@" \
  --require-arm A --require-arm B --require-arm C \
  --require-outcome findings --require-outcome clean --require-outcome stopped 2>&1 | head -20
echo "uniformity exit=$?"
exit $status
