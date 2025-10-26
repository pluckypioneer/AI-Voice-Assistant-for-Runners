from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum

from pydantic import BaseModel, Field, field_validator
from config.config import Config

router = APIRouter()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Mock user database (in production, use real database)
fake_users_db = {}

# Data Types
class DataTypeEnum(str, Enum):
    """Supported health data types"""
    SLEEP = "sleep"
    HRV = "hrv" 
    RUN = "run"

# Request/Response Models
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(...)
    password: str = Field(..., min_length=6)

class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str

class HealthDataIngestRequest(BaseModel):
    user_id: str = Field(...)
    data_type: DataTypeEnum = Field(...)
    data: Dict[str, Any] = Field(...)
    
    @field_validator('user_id', 'data_type', 'data')
    def not_empty(cls, v):
        if v is None or (isinstance(v, str) and v.strip() == ""):
            raise ValueError('must not be empty')
        return v

class HealthDataIngestResponse(BaseModel):
    message: str
    user_id: str
    data_type: DataTypeEnum
    received_at: str

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    return encoded_jwt

# Authentication endpoints
@router.post("/auth/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegisterRequest):
    """Register a new user"""
    if user_data.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    fake_users_db[user_data.username] = {
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": hashed_password,
        "disabled": False
    }
    
    return {
        "message": "User registered successfully",
        "username": user_data.username,
        "email": user_data.email
    }

@router.post("/auth/login", response_model=UserLoginResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user and return access token"""
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user["username"]}, 
        expires_delta=Config.JWT_ACCESS_TOKEN_EXPIRES
    )
    
    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        username=user["username"]
    )

# Data ingestion endpoint - 符合文档要求的路径 /api/v1/data/ingest
@router.post("/data/ingest", response_model=HealthDataIngestResponse)
async def ingest_health_data(data: HealthDataIngestRequest):
    """
    Receive health data from frontend (HealthKit data)
    
    Supported data types: sleep, hrv, run
    """
    return HealthDataIngestResponse(
        message="Data received successfully",
        user_id=data.user_id,
        data_type=data.data_type,
        received_at=datetime.utcnow().isoformat()
    )

# Health check endpoint
@router.get("/health")
async def health_check():
    return {
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }