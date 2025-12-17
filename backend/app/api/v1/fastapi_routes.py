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
from app.schemas import UserCreate, UserLogin, Token, FitnessDataUpload, RunAnalysisRequest, RunAnalysisResponse, RunHistoryItem
from typing import List

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

@router.post("/runs/analyze", response_model=RunAnalysisResponse)
def analyze_run(
    run_data: RunAnalysisRequest,
    db = Depends(get_db)
):
    # TEMPORARY: Hardcode user for testing without auth
    class DummyUser:
        id = 1
    current_user = DummyUser()

    # Simple v1 Model Logic
    insight = "Great run!"
    
    # Analyze distance
    if run_data.distance > 5.0:
        insight = "Impressive endurance! You ran over 5km."
    elif run_data.distance < 2.0:
        insight = "Good start! Short runs are great for recovery."
    
    # Analyze heart rate if available
    if run_data.heart_rate:
        if run_data.heart_rate > 160:
            insight += " Your heart rate was high, make sure to rest well."
        elif run_data.heart_rate < 120:
            insight += " You stayed in a comfortable aerobic zone."

    # Compare to history (simplified)
    # Fetch last run to compare
    last_runs = db.query(FitnessData).filter(
        FitnessData.user_id == current_user.id,
        FitnessData.data_type == "json"  # Assuming runs are stored as json
    ).order_by(FitnessData.created_at.desc()).limit(5).all()
    
    avg_dist = 0
    count = 0
    for run in last_runs:
        try:
            data = json.loads(run.data)
            if "distance" in data:
                avg_dist += float(data["distance"])
                count += 1
        except:
            continue
            
    if count > 0:
        avg_dist /= count
        if run_data.distance > avg_dist * 1.1:
            insight += f" You ran 10% further than your recent average of {avg_dist:.1f}km!"
    
    return {"insight": insight}

@router.get("/runs", response_model=List[RunHistoryItem])
def get_run_history(
    db = Depends(get_db)
):
    # TEMPORARY: Hardcode user for testing without auth
    current_user_id = 1

    # Fetch all JSON data which we assume contains runs
    fitness_data = db.query(FitnessData).filter(
        FitnessData.user_id == current_user_id,
        FitnessData.data_type == "json"
    ).order_by(FitnessData.created_at.desc()).all()
    
    history = []
    for item in fitness_data:
        try:
            data = json.loads(item.data)
            # Check if it looks like a run (has distance/duration)
            if "distance" in data and "duration" in data:
                history.append({
                    "id": item.id,
                    "date": item.created_at,
                    "distance": float(data["distance"]),
                    "duration": str(data["duration"]),
                    "avg_heart_rate": data.get("heartRate") or data.get("heart_rate")
                })
        except json.JSONDecodeError:
            continue
            
    return history

@router.post("/runs/save")
def save_run(
    run_data: RunAnalysisRequest,
    db = Depends(get_db)
):
    print(f"DEBUG: save_run called with {run_data}")
    # TEMPORARY: Hardcode user for testing
    class DummyUser:
        id = 1
    current_user = DummyUser()

    try:
        # Create run data object matching the structure we use in analysis/history
        data_to_save = {
            "duration": run_data.duration,
            "distance": run_data.distance,
            "heartRate": run_data.heart_rate,
            "stepCount": run_data.step_count,
            "timestamp": datetime.now().isoformat()
        }

        # Create fitness data record
        fitness_data = FitnessData(
            user_id=current_user.id,
            data_type="json",
            data=json.dumps(data_to_save)
        )
        
        db.add(fitness_data)
        db.commit()
        db.refresh(fitness_data)
        
        return {
            "message": "Run saved successfully",
            "id": fitness_data.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save run: {str(e)}")

@router.post("/health-data/save")
def save_daily_health_data(
    data: dict,  # Generic dict to accept any health structure
    db = Depends(get_db)
):
    # TEMPORARY: Hardcode user for testing
    class DummyUser:
        id = 1
    current_user = DummyUser()

    try:
        # Create fitness data record
        fitness_data = FitnessData(
            user_id=current_user.id,
            data_type="daily_summary",
            data=json.dumps(data)
        )
        
        db.add(fitness_data)
        db.commit()
        db.refresh(fitness_data)
        
        return {
            "message": "Health data saved successfully",
            "id": fitness_data.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save health data: {str(e)}")

@router.post("/health-data/upload")
def upload_health_data(
    file: UploadFile = File(...),
    db = Depends(get_db)
):
    # TEMPORARY: Hardcode user for testing without auth
    class DummyUser:
        id = 1
    current_user = DummyUser()

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
    db = Depends(get_db)
):
    # TEMPORARY: Hardcode user for testing without auth
    current_user_id = 1

    fitness_data = db.query(FitnessData).filter(
        FitnessData.user_id == current_user_id,
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