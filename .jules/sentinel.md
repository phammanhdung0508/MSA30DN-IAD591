## 2025-03-20 - [SQLi & CORS Fixes]
**Vulnerability:** SQL injection via f-string interpolation in `datetime` modifiers and insecure CORS configuration (allow_credentials=True with allow_origins=["*"]).
**Learning:** SQLite parameters cannot be used directly inside single quotes for modifiers like `datetime('now', '-? hours')`. They must be concatenated using the `||` operator: `datetime('now', '-' || ? || ' hours')`. Additionally, FastAPI/Starlette CORSMiddleware rejects `allow_credentials=True` if `allow_origins` is `["*"]` in modern browsers.
**Prevention:** Always use parameterized queries even for interval values. Ensure CORS settings comply with browser security models by disabling credentials when using wildcard origins.
