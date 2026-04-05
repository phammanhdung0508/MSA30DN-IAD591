## 2025-05-15 - Parameterizing SQLite `datetime()` Intervals
**Vulnerability:** SQL Injection in `apps/api/database.py` via f-string interpolation into SQLite's `datetime('now', '-{hours} hours')` function.
**Learning:** SQLite's `datetime` function doesn't directly support standard parameter markers (`?`) inside its string arguments (e.g., `datetime('now', '-? hours')` fails).
**Prevention:** Use SQLite's string concatenation operator (`||`) to safely inject parameters into function arguments: `datetime('now', '-' || ? || ' hours')`. This allows the driver to handle the value as a separate parameter while fulfilling the function's string format requirement.
