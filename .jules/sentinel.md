## 2025-03-22 - SQL Injection in Dynamic Time Intervals
**Vulnerability:** SQL Injection via f-string interpolation of `hours` and `days` parameters in `sqlite3` queries.
**Learning:** Even simple numeric parameters can be vectors for SQL injection if interpolated directly into a query string.
**Prevention:** Use standard `?` placeholders for parameters. For SQLite functions like `datetime()`, use string concatenation within the SQL: `datetime('now', '-' || ? || ' hours')`.

## 2025-03-22 - Insecure CORS with Wildcard Origin
**Vulnerability:** `CORSMiddleware` configured with `allow_origins=["*"]` and `allow_credentials=True`.
**Learning:** Browsers and security standards prohibit allowing credentials (cookies, auth headers) when the origin is a wildcard, as it presents a significant CSRF risk.
**Prevention:** Always set `allow_credentials=False` when using `allow_origins=["*"]`, or restrict origins to specific trusted domains.
