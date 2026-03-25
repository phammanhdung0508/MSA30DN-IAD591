## 2026-03-25 - [SQL Injection & CORS Security]
**Vulnerability:** SQL Injection in SQLite `datetime()` functions and insecure CORS wildcard origin with credentials.
**Learning:** Interpolating variables into SQLite `datetime('now', '-' || ? || ' hours')` requires using the concatenation operator `||` to safely parameterize the interval value. Wildcard origins in FastAPI's `CORSMiddleware` are risky when `allow_credentials=True` is set.
**Prevention:** Always use parameterized queries even for simple numeric intervals. Use environment variables for CORS origin configuration instead of hardcoded wildcards.
