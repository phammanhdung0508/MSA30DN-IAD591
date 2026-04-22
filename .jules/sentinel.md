## 2026-04-22 - Parameterized Time Intervals in SQLite
**Vulnerability:** Potential SQL injection via f-string interpolation of time intervals in SQLite `datetime()` functions.
**Learning:** Even when inputs are validated as integers in the API layer, using f-strings for SQL query construction violates defense-in-depth principles. SQLite doesn't support parameterizing the interval unit directly, but supports string concatenation with placeholders.
**Prevention:** Use the pattern `datetime('now', '-' || ? || ' hours')` and pass the numeric value as a parameter to ensure safe query execution.

## 2026-04-22 - Environment-Based CORS Configuration
**Vulnerability:** Hardcoded wildcard (`*`) in CORS allowed origins with `allow_credentials=True`.
**Learning:** Hardcoding `allow_origins=["*"]` is insecure for production as it allows any domain to make credentialed requests. Moving this to an environment variable provides flexibility and a path to a secure configuration.
**Prevention:** Load allowed origins from a `CORS_ALLOWED_ORIGINS` environment variable and provide a warning when falling back to a wildcard.
