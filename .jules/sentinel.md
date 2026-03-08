## 2026-03-08 - SQLite Parameterized Intervals and CORS Wildcard Incompatibility
**Vulnerability:** SQL Injection in analytics queries and insecure CORS configuration.
**Learning:** Developers often use f-strings for SQLite intervals (e.g., `datetime('now', '-{hours} hours')`) assuming they cannot be parameterized. However, SQLite string concatenation (`||`) allows safe parameterization of these values. Additionally, FastAPI's `CORSMiddleware` with `allow_origins=["*"]` is incompatible with `allow_credentials=True` according to browser security specs, leading to either non-functional CORS or potential credential leakage.
**Prevention:** Always use `?` placeholders with `||` for dynamic intervals in SQLite. Ensure `allow_credentials=False` when using wildcard origins in CORS.
