## 2025-05-14 - [CORS and SQL Parameterization Learnings]
**Vulnerability:** SQL injection via dynamic time intervals and insecure CORS configuration with `allow_credentials=True` and `allow_origins=["*"]`.
**Learning:** SQL parameterization is often missed for non-WHERE clause values like interval lengths in `datetime()`. In CORS, `allow_credentials=True` is incompatible with `allow_origins=["*"]` and poses a risk of credential leakage.
**Prevention:** Use SQL string concatenation with parameters for dynamic intervals. Always set `allow_credentials=False` when using wildcard origins in CORS.
