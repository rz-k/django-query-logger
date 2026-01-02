# Django Query Count Logging Middleware

A lightweight Django middleware to inspect **SQL query count**, **duplicate queries**, and **N+1 (similar) queries** directly in the terminal with **beautiful, colored, table-based output**.

Designed for ORM debugging when `DEBUG = True`.

---

## Features

- Total SQL query count per request
- Detect **duplicate queries**
- Detect **similar queries (N+1 problem)**
- Pretty terminal output using `rich`
- No browser UI required
- Works great for APIs

---

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```
Installation

1️⃣ Copy the Middleware File
Copy the middleware file into your Django project, for example:
```python
config/middleware/query_logger.py
```
You can place it anywhere you keep your custom middleware.

2️⃣ Add Middleware to settings.py
Add the middleware at the top of the MIDDLEWARE list:

```python
MIDDLEWARE = [
    "config.middleware.QueryCountLoggingMiddleware",
    *MIDDLEWARE,
]
```

⚠️ Important: 
It must be placed before other middleware to capture all ORM queries.

Usage
Start your Django server and hit any endpoint (API or page).

Example:

```bash
GET /api/kit/groups/
```
You will see output like:

Request path

Execution time

Total number of SQL queries

Duplicate queries table

Similar queries (N+1) table


Notes
Only active when DEBUG = True

Intended for development and debugging only

Not a replacement for Django Debug Toolbar

Especially useful for backend/API developers

Known Limitations
Does not show exact Python source line where the query was triggered
(Django Debug Toolbar uses internal DB instrumentation for this)
