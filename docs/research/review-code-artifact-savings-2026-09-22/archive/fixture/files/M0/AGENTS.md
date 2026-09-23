# Ledger

Standard-library Python 3.9+ only. Run the suite from the repository root with `python3 -m unittest discover -s tests -v`.

- Amounts are integer cents; never use floats for money.
- Every public function's docstring names the errors it raises.
- Authorization decisions live in `ledger/auth.py`; callers never compare roles themselves.
- A refused operation leaves every account unchanged.
