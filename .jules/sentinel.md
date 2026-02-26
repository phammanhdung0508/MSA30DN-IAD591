## 2026-02-12 - Parameterizing SQLite Time Intervals
**Vulnerability:** SQL injection via string interpolation of time interval values (hours, days) in the `datetime()` function.
**Learning:** Even when inputs are validated as integers in the API layer, using f-strings for SQL construction is a risk. In SQLite, the `datetime` function doesn't support parameters directly for the interval string (e.g., `datetime('now', ?)` where `?` is `'-24 hours'`).
**Prevention:** Use the SQLite concatenation pattern to safely inject variables: `datetime('now', '-' || ? || ' hours')`.

## 2026-02-12 - Secure CORS with Wildcards
**Vulnerability:** Insecure CORS configuration allowing credentials with a wildcard origin.
**Learning:** Modern browsers block requests where `Access-Control-Allow-Credentials` is `true` if `Access-Control-Allow-Origin` is `*`. This leads to a broken or insecure configuration.
**Prevention:** Always set `allow_credentials=False` when using `allow_origins=["*"]`.
