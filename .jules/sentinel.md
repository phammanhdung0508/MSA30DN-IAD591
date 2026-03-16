# Sentinel Journal - Critical Security Learnings

## 2025-05-23 - SQL Injection in SQLite Time Intervals
**Vulnerability:** SQL injection was possible by interpolating variables into SQLite `datetime` functions within f-strings.
**Learning:** SQLite allows parameterizing parts of a string by using the concatenation operator `||`. This is necessary for dynamic intervals like `datetime('now', '-' || ? || ' hours')`.
**Prevention:** Never use f-strings or string concatenation in Python to build SQL queries. Always use `?` placeholders and let the database driver handle parameterization.

## 2025-05-23 - Insecure CORS with Wildcard Origins
**Vulnerability:** FastAPI `CORSMiddleware` was configured with `allow_origins=["*"]` and `allow_credentials=True`.
**Learning:** Browsers and security standards prohibit sending credentials (cookies, Authorization headers) when the origin is a wildcard. This can lead to security vulnerabilities and is blocked by modern browsers.
**Prevention:** If `allow_origins` is `["*"]`, `allow_credentials` must be `False`. If credentials are required, specific origins must be listed.
