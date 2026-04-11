## 2026-04-11 - SQL Injection in SQLite datetime() and CORS hardening
**Vulnerability:** Several API endpoints in `apps/api/database.py` were using f-strings to interpolate integer parameters into SQL query strings, specifically within the `datetime('now', '-{hours} hours')` function call. This allowed for SQL injection if the input was not strictly validated as an integer before reaching the database layer. Additionally, `apps/api/main.py` had a hardcoded `allow_origins=["*"]` which is insecure when `allow_credentials=True`.

**Learning:** SQLite's `datetime()` function accepts modifiers as strings, which might tempt developers to use string interpolation. However, these modifiers can and should be parameterized like any other value in the `WHERE` clause.

**Prevention:** Always use `?` placeholders for any variable data in SQL queries, even for function arguments. Use environment variables for CORS configuration to avoid insecure defaults in production.
