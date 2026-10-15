# CI/CD (Phase 16)

## GitHub Actions Workflow (`ci.yml`)

The CI/CD pipeline is defined in `.github/workflows/ci.yml`. It runs automatically on `push` and `pull_request` to the `main` branch.

### Jobs Breakdown

1. **backend-tests**:
   - Runs on `ubuntu-latest`.
   - Uses Python 3.11 with `pip` caching.
   - **Dependencies**: Installs from `backend/requirements.txt`.
   - **Linting**: Uses `ruff` for fast and comprehensive code linting.
   - **Type Checking**: Uses `mypy` to ensure type safety in `app/`.
   - **Testing**: Runs `pytest` with verbosity enabled to validate backend functionality.

2. **frontend-build**:
   - Runs on `ubuntu-latest`.
   - Uses Node.js 20 with `npm` caching based on `package-lock.json`.
   - **Dependencies**: Runs `npm ci` for deterministic installs.
   - **Build**: Executes `npm run build` to verify the frontend compiles successfully without errors.

## Principles
- **Fail Fast**: By splitting backend and frontend into parallel jobs, we get faster feedback.
- **Reproducibility**: `npm ci` and pinned Python versions ensure builds are reproducible.
- **Quality Gates**: Ruff, Mypy, and Pytest serve as automated quality gates before any merge.
