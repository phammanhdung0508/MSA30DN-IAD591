## 2026-02-12 - Parameterizing SQLite Time Intervals
**Vulnerability:** SQL injection risk in `apps/api/database.py` due to f-string interpolation of time intervals (e.g., `hours`, `days`) in `datetime('now', '-{hours} hours')`.
**Learning:** Even when inputs are type-hinted as `int` and validated in the API layer, using f-strings in SQL queries is a dangerous pattern that can lead to vulnerabilities if the function is reused or if validation is bypassed.
**Prevention:** Always use parameterized queries. For SQLite time intervals, use the concatenation pattern: `datetime('now', '-' || ? || ' hours')` to safely bind the interval value.
