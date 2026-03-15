# Sentinel Journal

## 2025-05-15 - SQL Injection in SQLite datetime intervals
**Vulnerability:** Use of Python f-strings to interpolate variables into SQLite `datetime('now', ...)` intervals.
**Learning:** Even with type-hinted integers at the API level, string interpolation for SQL queries is a critical vulnerability. In SQLite, dynamic intervals can be safely parameterized using the concatenation operator `||`.
**Prevention:** Always use `?` placeholders for all dynamic values in SQL queries. For SQLite intervals, use the pattern `datetime('now', '-' || ? || ' units')`.

## 2025-05-15 - Insecure CORS with Wildcard Origin
**Vulnerability:** `CORSMiddleware` configured with `allow_origins=["*"]` and `allow_credentials=True`.
**Learning:** Browsers block CORS requests when both wildcard origins and credentials are enabled as it poses a significant security risk.
**Prevention:** Set `allow_credentials=False` when using `allow_origins=["*"]`, or specify explicit allowed origins if credentials are required.
