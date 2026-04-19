## 2026-04-19 - SQL Injection in Analytics and Insecure CORS

**Vulnerability:** SQL Injection via f-strings in `database.py` and overly permissive CORS in `main.py`.

**Learning:**

1. Several database functions (`get_sensor_summary`, `get_energy_analytics`, `get_temp_analytics`) used f-strings to inject time intervals directly into SQL queries. While the inputs were expected to be integers, they were passed from API endpoints without sufficient validation or parameterization, leading to potential SQL injection.
2. The FastAPI application used `allow_origins=["*"]` while having `allow_credentials=True`. This is a security risk as it allows any origin to make authenticated requests to the API.

**Prevention:**

1. Always use parameterized queries (`?` placeholders) for all variable parts of a SQL query. For dynamic intervals in SQLite, use string concatenation within the SQL: `datetime('now', '-' || ? || ' hours')`.
2. Restrict CORS origins to a known whitelist, ideally managed via environment variables. Avoid wildcards when credentials are enabled.
