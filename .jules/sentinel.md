## 2026-04-25 - SQL Injection in Analytics Functions
**Vulnerability:** SQL injection via f-strings in SQLite `datetime()` function calls.
**Learning:** Even with type hinting (e.g., `hours: int`), using f-strings for SQL query construction is dangerous. If the function is called from elsewhere without type checking or if a malicious string is passed, it leads to SQL injection. SQLite's `datetime()` doesn't allow standard parameterization for the interval string (e.g., `'? hours'`), requiring safe string concatenation within the SQL itself.
**Prevention:** Always use parameterized queries (`?` placeholders). For dynamic intervals in SQLite, use `||` concatenation like `datetime('now', '-' || ? || ' hours')`.

## 2026-04-25 - Insecure CORS and Missing Input Validation
**Vulnerability:** CORS configured with `allow_credentials=True` and wildcard origins; missing input length/range validation on API endpoints.
**Learning:** FastAPI's `CORSMiddleware` allows `allow_credentials=True` with `allow_origins=["*"]` in some versions, which is a security risk. Pydantic models without constraints can be exploited for DoS.
**Prevention:** Always dynamically disable `allow_credentials` if wildcard origins are used. Use Pydantic's `Field` and FastAPI's `Query`/`Path` for all user-facing inputs.
