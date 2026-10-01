#!/usr/bin/env python3
"""Open or close one attempt through the pinned ledger, for the P25 battery."""
from __future__ import annotations

import importlib.util
import sys


def main():
    budget_path, ledger, operation, attempt = sys.argv[1:5]
    spec = importlib.util.spec_from_file_location("pinned_budget", budget_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    config = {"attempt_id": attempt, "cell_id": "cell-" + attempt,
              "contexts": {"primary": "ctx-" + attempt}, "predecessor": None,
              "replacement_ordinal": 0}
    try:
        module.attempt_event(ledger, config,
                             close="complete" if operation == "close" else None)
    except module.Violation as violation:
        print(str(violation))
        return 1
    print(operation + " " + attempt + " accepted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
