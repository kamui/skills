#!/bin/sh
# Recreates the disposable fixture repository used for the item-3 and item-5 exercises on 2026-09-19.
# Usage: sh make_fixture.sh <target directory>
# The head commit implements `paginate` with a 0-based `start`, which contradicts spec.md's 1-based page
# rule while every test in test_pagination.py still passes: the defect is what a gate review must find.
set -eu
target=${1:?target directory}
mkdir -p "$target"
cd "$target"
git init -q -b main
git config user.email fixture@example.invalid
git config user.name Fixture

cat > README.md <<'EOF'
# pagination fixture

A tiny library with one function, `paginate`, described in `spec.md`.
Run the tests with `python3 -m unittest -v`.
EOF
cat > spec.md <<'EOF'
# Spec: paginate

Add `paginate(items, page, size)` in `pagination.py`.

- `page` is 1-based: page 1 holds the first `size` items of `items`, page 2 the next `size`, and so on.
- The last page may be shorter than `size`. A page past the end returns an empty list.
- `page < 1` or `size < 1` raises `ValueError`.
- Tests live in `test_pagination.py` and run with `python3 -m unittest -v` from the repository root.

Acceptance: the unit tests pass at the head being reviewed, and page 1 of `[10, 20, 30]` with size 2 is `[10, 20]`.
EOF
git add -A
git commit -q -m "Add the paginate spec"

cat > pagination.py <<'EOF'
"""Slice a sequence into fixed-size pages."""


def paginate(items, page, size):
    """Return the items on page ``page`` (1-based) when ``items`` is split into pages of ``size``."""
    if page < 1:
        raise ValueError("page must be >= 1")
    if size < 1:
        raise ValueError("size must be >= 1")
    start = page * size
    return list(items[start:start + size])
EOF
cat > test_pagination.py <<'EOF'
import unittest

from pagination import paginate


class PaginateTests(unittest.TestCase):
    def test_rejects_page_below_one(self):
        with self.assertRaises(ValueError):
            paginate([1, 2, 3], 0, 2)

    def test_rejects_size_below_one(self):
        with self.assertRaises(ValueError):
            paginate([1, 2, 3], 1, 0)

    def test_empty_source_gives_empty_page(self):
        self.assertEqual(paginate([], 1, 3), [])

    def test_page_past_the_end_is_empty(self):
        self.assertEqual(paginate([1, 2, 3, 4], 3, 2), [])

    def test_page_holds_at_most_size_items(self):
        self.assertEqual(len(paginate(list(range(10)), 1, 3)), 3)


if __name__ == "__main__":
    unittest.main()
EOF
git add -A
git commit -q -m "Implement paginate with 1-based pages"
git log --oneline
