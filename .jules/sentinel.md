## 2026-04-15 - SQL Injection in SQLite datetime() functions
**Vulnerability:** SQL injection was found in `apps/api/database.py` where user-provided time intervals (hours/days) were directly interpolated into SQL strings using f-strings, specifically within SQLite's `datetime()` function calls.
**Learning:** Even when parameters seem like simple integers, directly interpolating them into SQL queries creates a risk. In SQLite, parameterizing offsets in `datetime()` requires careful syntax like `datetime('now', '-' || ? || ' hours')`.
**Prevention:** Always use parameterized queries (?) for all user-provided inputs, including those used in SQL functions like `datetime` or `strftime`. Use string concatenation within the SQL query itself to safely combine placeholders with units.

## 2026-04-15 - Insecure CORS Configuration with Credentials
**Vulnerability:** The FastAPI application was configured with `allow_origins=["*"]` and `allow_credentials=True`, which is insecure and typically prohibited by browsers/frameworks when credentials are used.
**Learning:** Security defaults in frameworks like FastAPI often require explicit origin lists when credentials are enabled to prevent CSRF and other cross-origin attacks.
**Prevention:** Use environment variables to manage allowed origins in production and avoid wildcards when handling sensitive session information or credentials.
