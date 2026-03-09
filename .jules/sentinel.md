# Sentinel Journal 🛡️

## 2025-02-12 - SQL Injection in Analytics Queries
**Vulnerability:** Analytical database queries in `apps/api/database.py` were using f-string interpolation for `hours` and `days` parameters (e.g., `timestamp >= datetime('now', '-{hours} hours')`).
**Learning:** Even when inputs are typed as integers in the API layer, using string interpolation in SQL queries is a dangerous pattern that can lead to SQL injection if type enforcement is bypassed or if the pattern is copied to other areas with string inputs.
**Prevention:** Always use parameterized queries. For SQLite time intervals, use the concatenation pattern: `datetime('now', '-' || ? || ' hours')` where `?` is the placeholder for the parameter.

## 2025-02-12 - Insecure CORS Credential Sharing
**Vulnerability:** `CORSMiddleware` was configured with `allow_origins=["*"]` and `allow_credentials=True`.
**Learning:** Browsers block credentialed requests (cookies, Authorization headers) when the server responds with a wildcard `Access-Control-Allow-Origin: *`. This configuration is both insecure (potential for credential leakage if a browser quirk existed) and non-compliant with standard browser security policies.
**Prevention:** When using wildcard origins `*`, always set `allow_credentials=False`. If credentials are required, specific origins must be listed.
