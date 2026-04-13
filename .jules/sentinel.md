## 2025-05-15 - SQL Injection in SQLite datetime intervals
**Vulnerability:** SQL injection via f-string interpolation of numeric parameters into SQLite `datetime()` function calls.
**Learning:** Even if a parameter is expected to be an integer (e.g., `hours`), using f-strings to build queries is dangerous in Python because the type is not strictly enforced at runtime, and malicious strings can escape the query structure.
**Prevention:** Always use parameterized queries. For SQLite dynamic intervals, use string concatenation within the SQL: `datetime('now', '-' || ? || ' hours')`.

## 2025-05-15 - Insecure CORS Wildcard with Credentials
**Vulnerability:** Using `allow_origins=["*"]` with `allow_credentials=True` in FastAPI/Starlette CORSMiddleware.
**Learning:** While some frameworks block this combination, others might allow it or fail in ways that expose users to CSRF-like attacks if the browser's CORS policy is bypassed or misconfigured. It's a best practice to always specify allowed origins when credentials are involved.
**Prevention:** Use an environment variable to define a whitelist of allowed origins and parse it into a list for the CORS middleware.
