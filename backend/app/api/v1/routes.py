# Import necessary modules
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from datetime import datetime, timedelta
from math import ceil
from typing import List, Optional
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from app.api.v1.schemas import (
    UserDataSchema,
    UserRecord,
    WorkoutPoint,
    simplify_items,
)

# Create a Blueprint for v1 of the API
v1 = Blueprint('v1', __name__)


# Helpers
def isoformat_seconds(dt: datetime) -> str:
    """Return ISO 8601 format with seconds precision and 'Z'."""
    return dt.replace(microsecond=0).isoformat() + 'Z'


def success_response(data):
    return {"success": True, "data": data, "error": None}


def error_response(code: int, message: str):
    return {"success": False, "data": None, "error": {"code": code, "message": message}}


def parse_fields_param() -> Optional[List[str]]:
    fields_param = request.args.get('fields')
    if not fields_param:
        return None
    return [f.strip() for f in fields_param.split(',') if f.strip()]

# Health check endpoint
@v1.route('/health', methods=['GET'])
def health_check():
    # Returns the current status and timestamp of the application
    return jsonify(success_response({
        "status": "running",
        "timestamp": isoformat_seconds(datetime.utcnow()),
    }))

# Endpoint to receive user data
@v1.route('/user/data', methods=['POST'])
def user_data():
    # Receives and validates user data
    # Ensure the request contains a valid JSON body
    data = request.get_json(silent=True)
    if data is None:
        return jsonify(error_response(400, "Invalid or missing JSON body")), 400

    try:
        # Validate the incoming JSON data against the UserDataSchema
        UserDataSchema(**data)
        # Return a success message if the data is valid
        return jsonify(success_response({"message": "Data received successfully"}))
    except ValidationError as e:
        # Return a validation error message if the data is invalid
        msg = "Validation failed"
        return jsonify(error_response(400, msg)), 400


# Authentication endpoints
@v1.route('/auth/login', methods=['POST'])
def auth_login():
    payload = request.get_json(silent=True) or {}
    username = payload.get('username')
    password = payload.get('password')
    if not username or not password:
        return jsonify(error_response(403, "Permission denied: invalid credentials")), 403

    # Demo auth: accept fixed credentials; replace with real verification
    if not (username == 'demo' and password == 'demo123'):
        return jsonify(error_response(403, "Permission denied: invalid credentials")), 403

    identity = username
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    return jsonify(success_response({
        "access_token": access_token,
        "refresh_token": refresh_token
    }))


@v1.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def auth_refresh():
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify(success_response({"access_token": new_access_token}))


# List records endpoint with pagination and field selection
@v1.route('/user/records', methods=['GET'])
def user_records():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    fields = parse_fields_param()

    # Demo dataset
    total = 100
    all_items: List[UserRecord] = [
        UserRecord(user_id='u1', value=float(i), date=isoformat_seconds(datetime.utcnow() - timedelta(days=i)))
        for i in range(total)
    ]

    start = max((page - 1) * page_size, 0)
    end = min(start + page_size, total)
    page_items = all_items[start:end]

    simple_items = simplify_items(page_items, fields)
    resp = {
        "items": simple_items,
        "total": total,
        "pages": ceil(total / page_size) if page_size > 0 else 0
    }
    return jsonify(success_response(resp))


# Big data workout route endpoint with index slicing
@v1.route('/workout/route', methods=['GET'])
def workout_route():
    start_index = int(request.args.get('start_index', 0))
    end_index = request.args.get('end_index')
    end_index = int(end_index) if end_index is not None else None

    # Demo points dataset
    total_points = 1000
    points: List[WorkoutPoint] = [
        WorkoutPoint(lat=30.0 + i * 0.0001, lng=120.0 + i * 0.0001, ts=isoformat_seconds(datetime.utcnow()))
        for i in range(total_points)
    ]

    if end_index is None:
        end_index = min(start_index + 100, total_points)  # default batch size
    start_index = max(start_index, 0)
    end_index = min(end_index, total_points)
    if start_index >= end_index:
        return jsonify(error_response(400, "Invalid index range")), 400

    sliced = points[start_index:end_index]
    data = {
        "points": [p.model_dump() for p in sliced],
        "total": total_points,
        "range": {"start_index": start_index, "end_index": end_index}
    }
    return jsonify(success_response(data))


# Cached stats endpoint to reduce repeated computation
@v1.route('/user/stats', methods=['GET'])
def user_stats():
    cache = current_app.extensions.get('cache')
    user_id = request.args.get('user_id', 'u1')
    cache_key = f"stats:{user_id}"

    if cache:
        cached = cache.get(cache_key)
        if cached is not None:
            return jsonify(success_response(cached))

    # Simulate heavy computation
    total_sessions = 42
    avg_value = 12.34
    latest = isoformat_seconds(datetime.utcnow())
    result = {"user_id": user_id, "total_sessions": total_sessions, "avg_value": avg_value, "latest": latest}

    if cache:
        cache.set(cache_key, result, timeout=300)
    return jsonify(success_response(result))