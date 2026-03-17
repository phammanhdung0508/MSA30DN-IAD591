## 2025-05-14 - Parameterized Time Intervals in SQLite
**Vulnerability:** SQL injection via dynamic time intervals (e.g., `datetime('now', '-{hours} hours')`) using f-string interpolation in `apps/api/database.py`.
**Learning:** Even if input is typed as an integer, using string interpolation for any part of a SQL query is a dangerous pattern that can lead to injection if types are not strictly enforced at runtime. SQLite allows parameterizing modifiers via string concatenation within the query.
**Prevention:** Use the `'-' || ? || ' hours'` pattern with placeholders (`?`) for all dynamic interval parameters in SQLite queries.

## 2025-05-14 - Insecure CORS with Wildcard Origins
**Vulnerability:** `CORSMiddleware` configured with `allow_origins=["*"]` and `allow_credentials=True` in `apps/api/main.py`.
**Learning:** Browsers and modern frameworks (like Starlette/FastAPI) discourage or block the combination of wildcard origins and credentials to prevent sensitive data leakage (e.g., cookies) to arbitrary domains.
**Prevention:** Always set `allow_credentials=False` when using `allow_origins=["*"]`. If credentials are required, specify a list of trusted origins.
