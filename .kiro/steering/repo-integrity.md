---
inclusion: always
---
# Repository integrity

Rules learned from real incidents in this repo. Follow them to keep the
committed repository complete and runnable.

## Never git-ignore source packages
- `models/` is **core source** — it holds the Pydantic schemas (`models/schemas.py`)
  and shared enums (`models/enums.py`) that the entire backend imports. It must
  always be tracked. Never add it to `.gitignore`.
- More generally: do **not** add a directory to `.gitignore` because its name
  *looks* like data (e.g. `models/`, `checkpoints/`, `data/`). First confirm it is
  not a Python package. If it contains an `__init__.py` or `.py` source files, it
  is source and must be committed.
- Runtime/output dirs that are safe to ignore: `uploads/`, `generated/`, `logs/`,
  `.venv*/`, `node_modules/`, `web/dist/`, `__pycache__/`, and `_*` scratch files.

## Verify completeness after committing
- After the first commit of the project (or after any `.gitignore` change),
  confirm the repo is complete before relying on it:
  - `git ls-files models/` must be non-empty.
  - A fresh clone must import and build — the app must start without
    `ModuleNotFoundError`.

## "Done" means green CI, not a local pass
- A model-conversion change is **done** only when CI builds the deployment image
  and converts a real `.pt` and a real `.h5` to `conversion_status == "success"`
  inside the image. The green GitHub Actions run is the source of truth.
- A one-time local pass does not count — verify correctness locally first, then
  let CI be the permanent regression guard.
