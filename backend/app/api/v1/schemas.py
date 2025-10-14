from typing import List, Optional

# Import necessary modules
from pydantic import BaseModel, field_validator


# Pydantic schema for user data validation
class UserDataSchema(BaseModel):
    # User ID
    user_id: str
    # Data type
    data_type: str
    # Value of the data
    value: float

    # Validator to ensure that user_id, data_type, and value are not empty
    @field_validator('user_id', 'data_type', 'value')
    def not_empty(cls, v):
        if v is None or (isinstance(v, str) and v.strip() == ""):
            raise ValueError('must not be empty')
        return v


# Model representing a single user record
class UserRecord(BaseModel):
    user_id: str
    value: float
    date: str  # ISO 8601 without milliseconds, e.g., 2024-10-13T12:00:00Z


# Model representing a GPS point for workout route
class WorkoutPoint(BaseModel):
    lat: float
    lng: float
    ts: str  # ISO 8601 without milliseconds, e.g., 2024-10-13T12:00:00Z


# Helper for simplified responses: filter fields to reduce payload size
def simplify_items(items: List[BaseModel], fields: Optional[List[str]]) -> List[dict]:
    if not fields:
        return [item.model_dump() for item in items]
    include = set(fields)
    return [item.model_dump(include=include) for item in items]