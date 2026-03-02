## 2026-02-12 - Parameterizing Variable Time Intervals in SQLite
**Vulnerability:** SQL injection via f-string interpolation of numeric values (`hours`, `days`) into `datetime` function calls within SQLite queries.
**Learning:** Common parameterized query patterns (e.g., `?`) often fail in SQLite `datetime` functions if the entire interval string (e.g., `'-24 hours'`) isn't treated as a single literal. Developers often resort to f-string interpolation for convenience.
**Prevention:** Use the SQLite concatenation operator (`||`) to safely build the interval string within the SQL query, e.g., `datetime('now', '-' || ? || ' hours')`, passing the numeric value as a parameter.
