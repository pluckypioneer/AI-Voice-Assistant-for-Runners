from sqlalchemy import Column, Integer, String, DateTime, Float, PrimaryKeyConstraint
from app.db.base import Base

class PreparedData(Base):
    __tablename__ = "prepared_data"

    Id = Column(Integer, index=True) # Id is no longer the sole primary key
    ActivityDate = Column(DateTime)
    TotalSteps = Column(Integer)
    TotalDistance = Column(Float)
    TrackerDistance = Column(Float)
    LoggedActivitiesDistance = Column(Float)
    VeryActiveDistance = Column(Float)
    ModeratelyActiveDistance = Column(Float)
    LightActiveDistance = Column(Float)
    SedentaryActiveDistance = Column(Float)
    VeryActiveMinutes = Column(Integer)
    FairlyActiveMinutes = Column(Integer)
    LightlyActiveMinutes = Column(Integer)
    SedentaryMinutes = Column(Integer)
    Calories = Column(Integer)
    SleepDay = Column(DateTime)
    TotalSleepRecords = Column(Integer)
    TotalMinutesAsleep = Column(Integer)
    TotalTimeInBed = Column(Integer)
    RestingHeartRate = Column(Float)

    __table_args__ = (
        PrimaryKeyConstraint('Id', 'ActivityDate', name='prepared_data_pk'),
    )
