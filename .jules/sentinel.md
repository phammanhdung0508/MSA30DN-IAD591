## 2025-05-15 - SQL Injection and CORS Misconfiguration
**Vulnerability:** SQL injection via f-string interpolation in time interval parameters and CORS `allow_credentials=True` with wildcard origins.
**Learning:** Even internal parameters like `hours` or `days` passed from API endpoints to database queries can be exploited if not parameterized. FastAPI's `CORSMiddleware` blocks `allow_credentials=True` with `allow_origins=["*"]` in many modern browsers, but it's also a security risk.
**Prevention:** Always use `?` placeholders in SQLite queries, even for values within functions like `datetime()`. Set `allow_credentials=False` when using wildcard origins in CORS.
