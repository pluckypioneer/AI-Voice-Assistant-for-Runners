from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.config.config import Config
from app.db.base import get_db
from app.models.user import User
from app.models.fitness_data import FitnessData
from app.schemas import UserCreate, UserLogin, Token, FitnessDataUpload

router = APIRouter()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/auth/register", response_model=Token)
def register_user(user: UserCreate, db = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/health-data/upload")
def upload_health_data(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    try:
        # Read file content
        content = file.file.read()
        file.file.seek(0)  # Reset file pointer
        
        # For JSON files, parse and validate
        if file.content_type == "application/json":
            data = json.loads(content)
        else:
            # For binary files, encode as base64
            import base64
            data = base64.b64encode(content).decode('utf-8')
        
        # Create fitness data record
        fitness_data = FitnessData(
            user_id=current_user.id,
            data_type=file.filename.split('.')[-1],  # Use file extension as data type
            data=json.dumps(data) if isinstance(data, dict) else data
        )
        
        db.add(fitness_data)
        db.commit()
        db.refresh(fitness_data)
        
        return {
            "message": "File uploaded successfully",
            "file_id": fitness_data.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@router.get("/health-data/{data_type}")
def get_health_data(
    data_type: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    fitness_data = db.query(FitnessData).filter(
        FitnessData.user_id == current_user.id,
        FitnessData.data_type == data_type
    ).all()
    
    if not fitness_data:
        raise HTTPException(status_code=404, detail="No data found for this type")
    
    # Parse JSON data for JSON type records
    result = []
    for data in fitness_data:
        try:
            parsed_data = json.loads(data.data)
            result.append({
                "id": data.id,
                "data": parsed_data,
                "created_at": data.created_at
            })
        except json.JSONDecodeError:
            result.append({
                "id": data.id,
                "data": data.data,
                "created_at": data.created_at
            })
    
    return result

@router.get("/health")
def health_check():
    return {"status": "healthy"}