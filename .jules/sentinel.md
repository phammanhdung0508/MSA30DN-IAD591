## 2025-04-20 - SQL Injection in SQLite datetime() functions
**Vulnerability:** Use of f-strings to inject user-provided integers into `datetime('now', '-{hours} hours')` calls in SQLite queries.
**Learning:** Even when inputs are expected to be integers, using string interpolation for query building is a critical security risk. SQLite's `datetime()` function can be safely parameterized by using string concatenation within the SQL itself (e.g., `datetime('now', '-' || ? || ' hours')`).
**Prevention:** Always use parameterized queries (`?` placeholders) and never use f-strings or manual string formatting for SQL queries, even for non-string parameters.

## 2025-04-20 - Insecure CORS Wildcard with Credentials
**Vulnerability:** `CORSMiddleware` was configured with `allow_origins=["*"]` while `allow_credentials=True` was enabled.
**Learning:** Hardcoding a wildcard origin in CORS settings is a high security risk, especially when credentials (cookies, authorization headers) are allowed, as it can lead to CSRF-like attacks.
**Prevention:** Use environment variables to define allowed origins and default to a safe configuration or warn the developer if an insecure default is used.
