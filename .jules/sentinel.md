## 2025-05-15 - SQL Injection in SQLite time intervals
**Vulnerability:** Use of f-strings to inject time intervals into `datetime()` functions in SQLite queries.
**Learning:** Even when variables are typed (e.g., `int`), using string interpolation for SQL queries is a dangerous pattern. SQLite doesn't allow parameters directly inside the string literal of `datetime()`.
**Prevention:** Use SQL string concatenation to safely inject parameters into function arguments, e.g., `datetime('now', '-' || ? || ' hours')`.

## 2025-05-15 - Insecure CORS default with credentials
**Vulnerability:** FastAPI `CORSMiddleware` configured with `allow_origins=["*"]` while `allow_credentials=True`.
**Learning:** While FastAPI allows this, it is a security risk in production as it allows any site to make credentialed requests to the API.
**Prevention:** Use an environment variable to configure allowed origins and default to a restricted set or provide a loud warning if a wildcard is used in production-like environments.
