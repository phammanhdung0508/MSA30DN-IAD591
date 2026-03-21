## 2025-05-15 - SQL Injection in SQLite datetime functions
**Vulnerability:** SQL injection via f-string interpolation into SQLite `datetime('now', '-{hours} hours')`.
**Learning:** SQLite's `?` placeholder cannot be used directly inside single-quoted strings like `'-? hours'`. It must be concatenated using the `||` operator.
**Prevention:** Use the pattern `datetime('now', '-' || ? || ' hours')` for dynamic intervals in SQLite.

## 2025-05-15 - Insecure CORS with Wildcard Origin
**Vulnerability:** `allow_credentials=True` combined with `allow_origins=["*"]` in FastAPI `CORSMiddleware`.
**Learning:** Modern browsers block requests where both wildcard origins and credentials (cookies, auth headers) are enabled due to security risks.
**Prevention:** Always set `allow_credentials=False` when `allow_origins` is `["*"]`, or restrict origins to specific trusted domains.
