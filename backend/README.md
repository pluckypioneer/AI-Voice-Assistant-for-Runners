# Backend Service

This is the backend service for the AVAFR project.

## Project Structure

```
backend/
  ├─ app/
  │   ├─ main.py          # Project entry point (Flask app initialization, route registration, etc.)
  │   ├─ api/
  │   │   ├─ v1/
  │   │   │   ├─ routes.py  # Define API endpoint routes
  │   │   │   └─ schemas.py # Define request/response data formats (e.g., parameter validation, structure constraints)
  │   ├─ config/
  │   │   └─ config.py     # Configuration items (e.g., server port, environment variables)
  │   ├─ db/
  │   │   └─ base.py       # Basic database configuration (e.g., connection initialization template, no full implementation needed for now)
  │   ├─ models/           # Reserved directory for data models (no specific models to be implemented in this phase)
  │   └─ utils/            # Reserved directory for utility functions (e.g., common validation functions, can be empty in this phase)
  ├─ tests/                # Reserved directory for tests (can be empty or add a basic test example in this phase)
  ├─ requirements.txt      # Project dependency list
  └─ README.md             # Project documentation
```

## Local Startup Steps

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  Start the application:
    ```bash
    python app/main.py
    ```

The application will run at `http://localhost:5000`.

## API List

### Health Check

-   **URL**: `/api/v1/health`
-   **Method**: `GET`
-   **Description**: Checks the health of the service.
-   **Success Response**:
    ```json
    {
        "success": true,
        "data": {
            "status": "running",
            "timestamp": "<current_time>"
        },
        "error": null
    }
    ```
\n+## Windows Setup (py launcher)
\n+On Windows, you can use the `py` launcher to create and activate a virtual environment:
\n+1. Create virtual environment:
   ```powershell
   py -m venv venv
   ```
2. Activate virtual environment:
   ```powershell
   .\\venv\\Scripts\\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Start the application:
   ```powershell
   python app/main.py
   ```
\n+## API Usage Examples
\n+Health check:
```bash
curl http://localhost:5000/api/v1/health
```
\n+Submit valid user data:
```bash
curl -X POST http://localhost:5000/api/v1/user/data \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u1","data_type":"score","value":12.5}'
```
\n+Submit invalid user data (will return 400):
```bash
curl -X POST http://localhost:5000/api/v1/user/data \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u1","data_type":"score","value":"hello"}'
```
\n+Missing JSON body (will return 400):
```bash
curl -X POST http://localhost:5000/api/v1/user/data
```
\n+## Running Tests
\n+Install test dependencies and run pytest:
```bash
pip install -r requirements.txt
pytest -q
```

### User Data Reception

-   **URL**: `/api/v1/user/data`
-   **Method**: `POST`
-   **Description**: Receives user data.
-   **Request Body**:
    ```json
    {
        "user_id": "string",
        "data_type": "string",
        "value": "number"
    }
    ```
-   **Success Response**:
    ```json
    {
        "success": true,
        "data": {
            "message": "Data received successfully"
        },
        "error": null
    }
    ```

## Mobile Adaptation Notes

This backend is optimized for mobile scenarios with intermittent networks, limited bandwidth, and performance sensitivity. Key adaptations:

- Pagination for list endpoints: `page` (default `1`), `page_size` (default `20`). Responses include `total` and `pages`.
- Field filtering to reduce payload size: pass `fields` query parameter (comma-separated) to include only needed fields, e.g. `?fields=user_id,value,date`.
- Big data endpoints support index slicing: `start_index` and `end_index` allow chunked retrieval for GPS routes.
- Gzip compression: responses ≥ 1KB are automatically compressed when supported by client.
- Upload limit: server enforces `MAX_CONTENT_LENGTH = 10MB` to avoid blocking.
- Consistent datetime format: ISO 8601 ending with `Z`, second-level precision only (no milliseconds).
- Authentication: JWT-based with 1-hour access tokens and 7-day refresh tokens; silent refresh supported.
- Caching: heavy endpoints (e.g., stats) cached for 5 minutes to reduce repeated computation.

### Endpoint Examples

List user records with pagination and field filtering:
```bash
curl "http://localhost:5000/api/v1/user/records?page=2&page_size=10&fields=user_id,value,date"
```

Get workout route points in chunks:
```bash
curl "http://localhost:5000/api/v1/workout/route?start_index=0&end_index=200"
```

JWT login and refresh:
```bash
# Login (demo credentials)
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'

# Refresh (using refresh token)
curl -X POST http://localhost:5000/api/v1/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"
```

### Unified Response Format

All endpoints return a unified shape:
```json
{
  "success": true,
  "data": {},
  "error": null
}
```
On errors, `error` contains a code and a human-readable message:
```json
{
  "success": false,
  "data": null,
  "error": { "code": 401, "message": "Login expired, please sign in again" }
}
```

### Recommended Error Codes

- `401`: Token expired or invalid.
- `403`: Permission denied.
- `413`: Payload too large (upload exceeds 10MB).
-   **Error Response** (e.g., validation failed):
    ```json
    {
        "success": false,
        "data": null,
        "error": "Validation error: `user_id` is required."
    }
    ```