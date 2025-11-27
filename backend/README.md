# Backend Service

This is the backend service for the AVAFR project, built with FastAPI.

## Project Structure

```
backend/
  ├─ app/
  │   ├─ main_fastapi.py  # FastAPI entry point (primary)
  │   ├─ api/
  │   │   ├─ v1/
  │   │   │   ├─ routes.py          # Legacy Flask routes
  │   │   │   ├─ fastapi_routes.py  # FastAPI routes (primary)
  │   │   │   ├─ schemas.py         # Legacy Flask schemas
  │   │   │   └─ schemas_fastapi.py # FastAPI Pydantic models (primary)
  │   ├─ config/
  │   │   └─ config.py     # Configuration items (e.g., server port, environment variables)
  │   ├─ db/
  │   │   └─ base.py       # Basic database configuration
  │   ├─ models/           # Reserved directory for data models
  │   └─ utils/            # Reserved directory for utility functions
  ├─ tests/                # Test directory
  ├─ requirements.txt      # Project dependency list
  └─ README.md             # Project documentation
```

## Database Initialization

Before running the application, you need to initialize the database:

1.  Make sure you have configured the database connection string in `app/config/config.py`:
    ```python
    DATABASE_URL = "sqlite:///./av afr.db"
    ```

2.  Run the database initialization script:
    ```bash
    cd app && python -c "from db.base import Base, engine; Base.metadata.create_all(bind=engine)"
    ```

This will create the necessary tables in your database.

## Local Startup Steps

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  Initialize the database (see Database Initialization section above)

3.  Start the FastAPI application:
    ```bash
    cd app && python -m uvicorn main_fastapi:app --reload --host 0.0.0.0 --port 8000
    ```

Or using the py launcher on Windows:
```bash
cd app && py -m uvicorn main_fastapi:app --reload --host 0.0.0.0 --port 8000
```

The application will run at `http://localhost:8000` with automatic API documentation at `http://localhost:8000/docs`.

## API List

### Health Check

-   **URL**: `/api/v1/health`
-   **Method**: `GET`
-   **Description**: Checks the health of the service.
-   **Success Response**:
    ```json
    {
        "status": "running",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }
    ```

## Windows Setup (py launcher)

On Windows, you can use the `py` launcher to create and activate a virtual environment:
1. Create virtual environment:
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
4. Initialize the database (see Database Initialization section above)
5. Start the FastAPI application:
   ```powershell
   cd app && py -m uvicorn main_fastapi:app --reload --host 0.0.0.0 --port 8000
   ```

## API Usage Examples

### Health check:
```bash
curl http://localhost:8000/api/v1/health
```

### User registration:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'
```

### User login:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

### Submit health data:
```bash
curl -X POST http://localhost:8000/api/v1/data/ingest \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"data_type":"sleep","data":{"duration":480,"quality":85}}'
```

### Query health data:
```bash
curl -X GET http://localhost:8000/api/v1/data/query/1 \
  -H "Content-Type: application/json"
```

## Running Tests

Install test dependencies and run pytest:
```bash
pip install -r requirements.txt
pytest -q
```

### User Authentication

#### Register User
-   **URL**: `/api/v1/auth/register`
-   **Method**: `POST`
-   **Description**: Register a new user
-   **Request Body**:
    ```json
    {
        "username": "string",
        "email": "string",
        "password": "string"
    }
    ```
-   **Success Response**:
    ```json
    {
        "message": "User registered successfully",
        "user_id": 1,
        "username": "testuser",
        "email": "test@example.com"
    }
    ```

#### Login User
-   **URL**: `/api/v1/auth/login`
-   **Method**: `POST`
-   **Description**: Login user and get access token
-   **Request Body**:
    ```json
    {
        "username": "string",
        "password": "string"
    }
    ```
-   **Success Response**:
    ```json
    {
        "access_token": "jwt_token_here",
        "token_type": "bearer",
        "username": "testuser"
    }
    ```

### Health Data Operations

#### Submit Health Data
-   **URL**: `/api/v1/data/ingest`
-   **Method**: `POST`
-   **Description**: Receives health data from frontend (HealthKit data)
-   **Request Body**:
    ```json
    {
        "user_id": 1,
        "data_type": "sleep | hrv | run",
        "data": {
            "key": "value"
        }
    }
    ```
-   **Success Response**:
    ```json
    {
        "message": "Data received successfully",
        "user_id": 1,
        "data_type": "sleep",
        "received_at": "2024-01-01T00:00:00Z"
    }
    ```

#### Query Health Data
-   **URL**: `/api/v1/data/query/{user_id}`
-   **Method**: `GET`
-   **Description**: Query all health data for a specific user
-   **Success Response**:
    ```json
    [
        {
            "id": 1,
            "user_id": 1,
            "data_type": "sleep",
            "data": {
                "duration": 480,
                "quality": 85
            },
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
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