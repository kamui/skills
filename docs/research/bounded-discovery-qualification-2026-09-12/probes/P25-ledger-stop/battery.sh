#!/bin/sh
# P25: exercise the ledger's terminal stop on a real ledger and record what it refuses.
# Each step prints "STEP <name> exit=<code>" followed by the operation's own output.
set -u
BUD="$1"
LEDGER=stop-ledger.json
step() {
  name="$1"; shift
  out=$("$@" 2>&1); code=$?
  echo "STEP $name exit=$code"
  echo "$out" | head -2 | sed 's/^/    /'
}
python3 "$BUD" "$LEDGER" cap-freeze --amount 1.00 --reserve 0.30 --ticket 207 \
  --evidence probes/P25-ledger-stop > /dev/null 2>&1
step 01-reserve-outstanding      python3 "$BUD" "$LEDGER" reserve --id R1 --amount 0.10 --phase pre-freeze --ticket 207 --evidence probes/P25-ledger-stop
step 02-reserve-to-settle        python3 "$BUD" "$LEDGER" reserve --id R2 --amount 0.10 --phase pre-freeze --ticket 207 --evidence probes/P25-ledger-stop
step 03-settle-with-uncertainty  python3 "$BUD" "$LEDGER" settle  --id R2 --amount 0.04 --uncertainty 0.02 --ticket 207 --evidence probes/P25-ledger-stop
step 04-open-an-attempt          python3 attempt.py "$BUD" "$LEDGER" open A
step 05-stop                     python3 "$BUD" "$LEDGER" stop --reason "P25 probe: terminal stop with an outstanding reservation, retained uncertainty and one open attempt" --evidence probes/P25-ledger-stop/battery-output.txt --ticket 207
step 06-settle-after-stop        python3 "$BUD" "$LEDGER" settle --id R1 --amount 0.05 --uncertainty 0.01 --ticket 207 --evidence probes/P25-ledger-stop
step 07-close-attempt-after-stop python3 attempt.py "$BUD" "$LEDGER" close A
step 08-new-review-reservation   python3 "$BUD" "$LEDGER" reserve --id R3 --amount 0.05 --phase review --ticket 207 --evidence probes/P25-ledger-stop
step 09-new-pre-freeze-reserve   python3 "$BUD" "$LEDGER" reserve --id R4 --amount 0.05 --phase pre-freeze --ticket 207 --evidence probes/P25-ledger-stop
step 10-protected-grading        python3 "$BUD" "$LEDGER" reserve --id R5 --amount 0.05 --phase grading --ticket 207 --evidence probes/P25-ledger-stop
step 11-new-attempt-after-stop   python3 attempt.py "$BUD" "$LEDGER" open B
step 12-second-stop              python3 "$BUD" "$LEDGER" stop --reason "a second stop" --evidence probes/P25-ledger-stop --ticket 207
echo "--- retained after the stop ---"
python3 -c "
import json
d = json.load(open('$LEDGER'))
print('actual', d['actual_usd'], '| reserved', d['reserved_usd'], '| uncertainty', d['uncertainty_usd'])
print('events', len(d['events']), '| stops', sum(e['operation'] == 'stop' for e in d['events']))
stop = [e for e in d['events'] if e['operation'] == 'stop'][0]
print('stop ticket', stop['ticket'], '| reason retained:', stop['reason'][:60])
print('stop evidence retained:', stop['rate_usage_evidence'])
"
