from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class FitnessDataUpload(BaseModel):
    data_type: str
    data: str

class RunAnalysisRequest(BaseModel):
    distance: float  # in km
    duration: str    # "HH:MM:SS" or seconds
    heart_rate: Optional[int] = None
    step_count: Optional[int] = None

class RunAnalysisResponse(BaseModel):
    insight: str

class RunHistoryItem(BaseModel):
    id: int
    date: datetime
    distance: float
    duration: str
    avg_heart_rate: Optional[int] = None