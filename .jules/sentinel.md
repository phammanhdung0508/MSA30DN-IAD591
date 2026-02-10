## 2025-05-15 - SQL Injection in SQLite Time Intervals
**Vulnerability:** SQL injection vulnerability via f-string interpolation of time interval values (e.g., `hours`, `days`) in `datetime()` functions.
**Learning:** SQLite's `datetime()` function does not directly accept parameters for its modifiers (like `'-24 hours'`). Developers might be tempted to use f-strings to build these strings, introducing injection risks if the input is not strictly validated.
**Prevention:** Use SQLite string concatenation (`||`) within the SQL query to safely combine a parameter with a literal suffix, e.g., `datetime('now', '-' || ? || ' hours')`. This ensures the input is treated as a parameter and not part of the SQL command.
