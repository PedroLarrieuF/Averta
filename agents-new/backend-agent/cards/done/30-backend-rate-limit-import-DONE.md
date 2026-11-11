---
id: 30
title: "Fix Rate Limit Module Test Import"
priority: high
type: bug
agent: backend
sprint: 1
estimate: S
status: done
created: 2026-11-03
reviewed_by: techlead
---

# Card #30: Fix Rate Limit Module Test Import

## Description
Fix the failing test import for `app.core.rate_limit` module. The test is trying to import a module that either doesn't exist or has a different path.

## Error
```
ImportError: cannot import name 'RateLimiter' from 'app.core.rate_limit'
```

## Acceptance Criteria

### Investigation
- [ ] Check if `backend/app/core/rate_limit.py` exists
- [ ] Check what's exported from the module
- [ ] Check the test file that's failing
- [ ] Determine if module needs to be created or import path fixed

### Fix Options

#### Option A: Module Exists but Wrong Export
- [ ] Fix export in `rate_limit.py` (add `__all__` or fix class name)
- [ ] Fix import in test file

#### Option B: Module Doesn't Exist (Most Likely)
- [ ] Create `backend/app/core/rate_limit.py` with Redis-backed rate limiter
- [ ] Use `slowapi` as specified in Card #04 (already DONE)
- [ ] Export `RateLimiter` class

#### Option C: Test Import Path Wrong
- [ ] Fix import path in test (e.g., `from app.core.middleware import RateLimiter`)

### Implementation (if creating module)

Based on Card #04 (Rate Limiter Redis - DONE), the rate limiter should already be implemented. Check where it actually lives.

```python
# backend/app/core/rate_limit.py (if needs creation)
"""
Redis-backed rate limiter using slowapi.
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, FastAPI
from app.core.config import settings

# Redis-backed limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    default_limits=["100/minute"]
)

class RateLimiter:
    """Wrapper for slowapi limiter."""
    
    def __init__(self, app: FastAPI = None):
        self.limiter = limiter
        if app:
            self.init_app(app)
    
    def init_app(self, app: FastAPI):
        app.state.limiter = self.limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    def limit(self, limit_string: str):
        return self.limiter.limit(limit_string)

# Global instance
rate_limiter = RateLimiter()
```

### Files to Check/Modify
- `backend/app/core/rate_limit.py` - Create or fix
- `backend/app/core/middleware.py` - May already have rate limiting
- `backend/app/main.py` - Where limiter is initialized
- `backend/tests/` - Find the failing test file

### Verification
```bash
cd backend

# Test import works
poetry run python -c "from app.core.rate_limit import RateLimiter; print('Import OK')"

# Run the specific failing test
poetry run pytest tests/ -k "rate_limit" -v

# Run full test suite
poetry run test-cov
```

## Dependencies
- Card #04: Rate Limiter Redis (DONE - slowapi + Redis implemented)
- Card #28: Fix Failing Rule Tests (related - same test run)

## Testing Requirements
- Import test passes
- Rate limiting functionality works in integration tests
- No regression in existing rate limiting

## Definition of Done
- [ ] Import error resolved
- [ ] Rate limiter module exists and exports `RateLimiter`
- [ ] Related test passes
- [ ] Full test suite passes: `poetry run test-cov`
- [ ] Card moved to `review/`

## Notes
- Card #04 (Rate Limiter Redis) is marked DONE, so the implementation likely exists somewhere
- Check `app/core/middleware.py` or `app/main.py` for existing slowapi integration
- The test may be old/outdated - verify what the test is actually testing
- If rate limiting is already working via middleware, the test may just need import path update