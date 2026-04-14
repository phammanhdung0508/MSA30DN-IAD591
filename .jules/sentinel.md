## 2025-05-15 - SQL Injection via Time Interval Parameters
**Vulnerability:** Dynamic SQL query construction using f-strings for `hours` and `days` parameters in SQLite `datetime()` functions.
**Learning:** Even when parameters are expected to be integers, using string interpolation in SQL queries creates a risk if the input is not strictly validated or if the type system is bypassed. SQLite's `datetime` function interval strings are often overlooked as injection points.
**Prevention:** Always use parameterized queries (?) for all user-supplied data, including values intended for function arguments. For SQLite intervals, use string concatenation within the SQL (e.g., `'-' || ? || ' hours'`) to safely bind the numeric part.
