## 2026-03-10 - Parameterized Time Intervals and CORS Security

**Vulnerability:** SQL Injection via f-string interpolation in `apps/api/database.py` and Insecure CORS settings in `apps/api/main.py`.

**Learning:** Database queries using f-string interpolation for variable time intervals (e.g., `hours`, `days`) were susceptible to SQL injection. In FastAPI, `allow_credentials=True` with `allow_origins=['*']` is a common but insecure configuration that can leak sensitive data.

**Prevention:** Always use parameterized queries for all dynamic input. In SQLite, dynamic time intervals can be safely handled by concatenating placeholders (e.g., `'-' || ? || ' hours'`). For CORS, ensure `allow_credentials` is `False` when using wildcard origins, or restrict origins to specific trusted domains.
