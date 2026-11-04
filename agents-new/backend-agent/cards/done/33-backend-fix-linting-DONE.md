---
id: 33
title: "Fix Linting Issues (ruff)"
priority: medium
type: tech-debt
agent: backend
sprint: 3
estimate: M
status: ready
created: 2026-11-03
reviewed_by: techlead
---

# Card #33: Fix Linting Issues (ruff)

## Description
Fix 200+ ruff linting issues across the backend codebase. These are style/quality issues that don't affect functionality but should be resolved to maintain code quality and enable CI enforcement.

## Current Linting Status (2026-11-03)
- **Total issues**: 200+ across 159 files
- **Main categories**: Import sorting (I001), Deprecated typing (UP035/UP006), Unused imports (F401), Missing trailing newlines (W292), Print statements (T201), Module-level imports not at top (E402), Optional[X] vs X|None (UP045), Too many arguments (PLR0913/PLR0917), Commented-out code (ERA001), Global statements (PLW0603)

## Acceptance Criteria

### Import Sorting (I001)
- [ ] Organize imports in all files per ruff standards (stdlib → third-party → local)
- [ ] Run `ruff check --select I001 --fix` and verify

### Deprecated Typing (UP035, UP006, UP045)
- [ ] Replace `typing.List` → `list`, `typing.Dict` → `dict`, `typing.Optional` → `X | None`
- [ ] Replace `typing.Callable` → `collections.abc.Callable`
- [ ] Replace `Optional[str]` → `str | None` etc.

### Unused Imports (F401)
- [ ] Remove unused imports (`starlette.responses.JSONResponse`, `typing.Dict`, `typing.Any`, etc.)

### Missing Trailing Newlines (W292)
- [ ] Add trailing newlines to all files

### Print Statements (T201)
- [ ] Remove or replace `print()` in `app/core/celery_app.py:67` with proper logging

### Module-Level Imports Not at Top (E402)
- [ ] Move imports to top of file in:
  - `app/core/middleware.py` (ContextVar import)
  - `app/core/database.py` (Prisma import inside function)
  - `app/main.py` (exception handler imports)
  - `app/modules/documents/service.py` (NotificationsService import)
  - `app/modules/notifications/router.py` (multiple inline imports)

### Too Many Arguments (PLR0913, PLR0917)
- [ ] Refactor functions with >5 parameters (consider dataclasses, Pydantic models, or parameter objects)
- [ ] Key files: `app/core/security.py` (create_access_token), `app/modules/documents/service.py` (list_documents), `app/modules/notifications/router.py` (list_notifications)

### Commented-Out Code (ERA001)
- [ ] Remove commented-out code in:
  - `app/core/config.py` (SendGrid, Monitoring comments)
  - `app/main.py` (audit_router import)

### Global Statements (PLW0603)
- [ ] Refactor `app/core/database.py` to avoid global `prisma` variable (use dependency injection or singleton pattern)

## Technical Requirements

### Commands to Run
```bash
cd backend

# Check current issues
python -m ruff check .

# Auto-fix what's possible
python -m ruff check --fix .

# Format code
python -m ruff format .

# Check specific categories
python -m ruff check --select I001 .
python -m ruff check --select UP035,UP006,UP045 .
python -m ruff check --select F401 .
python -m ruff check --select W292 .
python -m ruff check --select T201 .
python -m ruff check --select E402 .
python -m ruff check --select PLR0913,PLR0917 .
python -m ruff check --select ERA001 .
python -m ruff check --select PLW0603 .
```

### Quality Gates (Must Pass)
```bash
python -m ruff check .          # Zero errors
python -m ruff format --check . # Zero formatting issues
python -m mypy .                # Type checking (after typing fixes)
python -m pytest tests/ -v      # All tests still pass
```

## Dependencies
- Card #28: Fix Failing Rule Tests (DONE - tests must still pass after refactoring)
- Card #30: Rate Limit Module (DONE - tests must still pass)

## Files to Focus On (Priority Order)
1. `app/core/config.py` - Many typing issues, commented code
2. `app/core/security.py` - Too many args, Optional→X|None
3. `app/core/middleware.py` - Import order, E402
4. `app/core/celery_app.py` - Print statement, import order
5. `app/core/database.py` - Global statement, inline import
6. `app/main.py` - E402, commented code
7. `app/modules/users/router.py` - Import order
8. `app/modules/documents/service.py` - Inline import, too many args
9. `app/modules/notifications/router.py` - Multiple inline imports, too many args
10. `app/core/rate_limit.py` - Import order
11. All other files with I001 issues

## Definition of Done
- [ ] `python -m ruff check .` returns zero errors
- [ ] `python -m ruff format --check .` returns zero issues
- [ ] `python -m mypy .` passes (no new typing errors)
- [ ] `python -m pytest tests/ -v` all 61 tests pass
- [ ] Card moved to `review/`

## Notes
- This is a tech-debt card - can be done incrementally
- Focus on auto-fixable issues first (I001, UP035/UP006, W292)
- Manual fixes needed for: E402, PLR0913, PLW0603, ERA001
- Run tests frequently to ensure no regressions
- Consider doing this in multiple PRs if scope is too large