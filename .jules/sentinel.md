## 2026-02-12 - Parameterized SQL Intervals in SQLite
**Vulnerability:** SQL injection via dynamic time interval parameters in SQLite queries using f-strings.
**Learning:** SQLite's `datetime` function can safely handle parameters if they are concatenated within the SQL expression using the `||` operator, e.g., `datetime('now', '-' || ? || ' hours')`.
**Prevention:** Always use `?` placeholders for any user-controlled input in SQL queries, even for values that are part of SQLite-specific function arguments like time intervals.

## 2026-02-12 - Wildcard CORS Security Compliance
**Vulnerability:** Insecure CORS configuration using `allow_origins=["*"]` with `allow_credentials=True`.
**Learning:** Modern browsers and security standards forbid sending credentials (cookies, authorization headers) when a wildcard origin is used. This configuration is insecure and typically fails in the browser.
**Prevention:** When using `allow_origins=["*"]`, always set `allow_credentials=False`. If credentials are required, specific allowed origins must be explicitly listed.
