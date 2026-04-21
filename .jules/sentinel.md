## 2025-05-15 - Parameterized SQL Intervals in SQLite
**Vulnerability:** SQL injection via f-strings in SQLite `datetime()` function calls for time intervals.
**Learning:** SQLite's `datetime('now', '-{hours} hours')` cannot be directly parameterized as `datetime('now', '-? hours')` because placeholders are for values, not part of strings.
**Prevention:** Use SQLite string concatenation `||` to safely build the interval string: `datetime('now', '-' || ? || ' hours')`. This allows the numeric value to be properly parameterized.
