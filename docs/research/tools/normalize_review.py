#!/usr/bin/env python3
"""Forwarding stub: this tool moved to bench/tools/normalize_review.py on 2026-09-24.

Historical bundles cite this path; the stub keeps those commands working.
Exit codes and output are the moved tool's own.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

_TARGET = Path(__file__).resolve().parents[3] / "bench" / "tools" / "normalize_review.py"
_spec = importlib.util.spec_from_file_location("normalize_review", _TARGET)
_module = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("normalize_review", _module)
_spec.loader.exec_module(_module)
globals().update({k: v for k, v in vars(_module).items() if not k.startswith("__")})

if __name__ == "__main__":
    sys.exit(_module.main())
