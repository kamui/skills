"""Exact outcome rates of this run's decision rule, and of #380's literal rule, under assumed rates.

Usage:
    python3 -B simulate.py

Adopted rule (README.md, "Decision rule"): the variant is rejected when, on the buggy target, its
registered-defect recoveries summed over three reviews are at least 2 below the control's, or when,
on the clean target, the number of its reviews carrying a false finding is at least 2 above the
control's. Otherwise it passes.

#380's literal rule, which the maintainer replaced before the freeze: the variant passes only when
its recoveries are at least the control's and its clean reviews carry no false finding. A clean
false finding when the control also carries one is inconclusive rather than a reject.

Rates on unseen targets are unknown, so the table sweeps them. Each registered defect is recovered
independently per review at rate r, and each clean review carries a false finding at rate f.
Everything is exact binomial arithmetic; nothing is sampled. Exit 0.
"""
import math
import sys

REPLICATES = 3
RECALL_MARGIN = 2
FALSE_MARGIN = 2


def binomial(n, p):
    return [math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]


def joint(n, p_control, p_variant, keep):
    control, variant = binomial(n, p_control), binomial(n, p_variant)
    return sum(pc * pv for c, pc in enumerate(control) for v, pv in enumerate(variant) if keep(c, v))


def adopted_pass(defects, r_control, r_variant, f_control, f_variant):
    recall = joint(REPLICATES * defects, r_control, r_variant, lambda c, v: c - v < RECALL_MARGIN)
    false = joint(REPLICATES, f_control, f_variant, lambda c, v: v - c < FALSE_MARGIN)
    return recall * false


def literal_outcome(defects, r_control, r_variant, f_control, f_variant):
    holds = joint(REPLICATES * defects, r_control, r_variant, lambda c, v: v >= c)
    variant_clean = (1 - f_variant) ** REPLICATES
    control_clean = (1 - f_control) ** REPLICATES
    passes = holds * variant_clean
    inconclusive = holds * (1 - variant_clean) * (1 - control_clean)
    return passes, 1 - passes - inconclusive


SCENARIOS = (("no effect", 1.0, 0.0), ("recall x0.8", 0.8, 0.0), ("recall x0.6", 0.6, 0.0),
             ("recall x0.3", 0.3, 0.0), ("false +0.33", 1.0, 1 / 3))


def main():
    print("Rejection rate, three replicates per arm on one buggy and one clean target.")
    print("Each cell reads adopted / #380 literal. r: per-review recovery rate per defect; f: control's")
    print("per-review false-finding rate on the clean target.\n")
    print("defects  f      r    " + "  ".join(f"{label:>15s}" for label, _, _ in SCENARIOS))
    for defects in (1, 2):
        for f in (1 / 30, 1 / 15, 1 / 6):
            for r in (0.3, 0.5, 0.7, 0.9):
                cells = []
                for _, loss, extra in SCENARIOS:
                    args = (defects, r, r * loss, f, min(1.0, f + extra))
                    cells.append(f"{1 - adopted_pass(*args):5.1%} / {literal_outcome(*args)[1]:5.1%}")
                print(f"{defects:7d}  {f:.3f}  {r:.1f}  " + "  ".join(f"{cell:>15s}" for cell in cells))
    return 0


if __name__ == "__main__":
    sys.exit(main())
