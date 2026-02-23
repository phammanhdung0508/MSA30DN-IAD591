## 2026-02-23 - SQLite Time Interval Parameterization
**Vulnerability:** SQL injection via string interpolation in SQLite `datetime()` function intervals.
**Learning:** SQLite parameters (?) cannot be used directly inside a string literal like `'-? hours'`.
**Prevention:** Use SQLite string concatenation `'-' || ? || ' hours'` to safely parameterize variable intervals.
