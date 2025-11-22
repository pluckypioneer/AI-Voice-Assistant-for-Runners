import pandas as pd
from sqlalchemy.orm import sessionmaker
from app.db.base import Base, engine
from app.models.prepared_data import PreparedData
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def seed_prepared_data():
    """
    Seeds the database with prepared data from prepared_data.csv using SQLAlchemy.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        prepared_data_path = os.path.join(script_dir, 'prepared_data.csv')

        # Explicitly drop the table before creating it to ensure schema updates
        PreparedData.__table__.drop(engine, checkfirst=True)
        logging.info("Dropped existing 'prepared_data' table (if any).")

        # Create all tables defined in Base (including PreparedData)
        Base.metadata.create_all(bind=engine)
        logging.info("Database tables created/updated.")

        logging.info(f"Loading prepared data from {prepared_data_path}...")
        df = pd.read_csv(prepared_data_path)
        logging.info("Prepared data loaded successfully.")

        # Convert relevant columns to datetime objects
        df['ActivityDate'] = pd.to_datetime(df['ActivityDate'])
        df['SleepDay'] = pd.to_datetime(df['SleepDay'])

        Session = sessionmaker(bind=engine)
        session = Session()
        logging.info("SQLAlchemy session created.")

        # Clear existing data in the prepared_data table before inserting (redundant after drop, but good for safety)
        # session.query(PreparedData).delete()
        # session.commit()
        # logging.info("Cleared existing data from 'prepared_data' table.")

        # Insert data row by row
        for index, row in df.iterrows():
            prepared_data_instance = PreparedData(
                Id=row['Id'],
                ActivityDate=row['ActivityDate'],
                TotalSteps=row['TotalSteps'],
                TotalDistance=row['TotalDistance'],
                TrackerDistance=row['TrackerDistance'],
                LoggedActivitiesDistance=row['LoggedActivitiesDistance'],
                VeryActiveDistance=row['VeryActiveDistance'],
                ModeratelyActiveDistance=row['ModeratelyActiveDistance'],
                LightActiveDistance=row['LightActiveDistance'],
                SedentaryActiveDistance=row['SedentaryActiveDistance'],
                VeryActiveMinutes=row['VeryActiveMinutes'],
                FairlyActiveMinutes=row['FairlyActiveMinutes'],
                LightlyActiveMinutes=row['LightlyActiveMinutes'],
                SedentaryMinutes=row['SedentaryMinutes'],
                Calories=row['Calories'],
                SleepDay=row['SleepDay'],
                TotalSleepRecords=row['TotalSleepRecords'],
                TotalMinutesAsleep=row['TotalMinutesAsleep'],
                TotalTimeInBed=row['TotalTimeInBed'],
                RestingHeartRate=row['RestingHeartRate']
            )
            session.add(prepared_data_instance)
            if index % 1000 == 0: # Commit in batches
                session.commit()
                logging.info(f"Committed {index + 1} rows.")
        
        session.commit()
        logging.info(f"Inserted all {len(df)} rows into 'prepared_data' table.")
        session.close()
        logging.info("Database seeding completed successfully.")

    except FileNotFoundError as e:
        logging.error(f"Error: {e}. Make sure 'prepared_data.csv' exists.")
    except Exception as e:
        logging.error(f"An error occurred during database seeding: {e}")
        session.rollback() # Rollback in case of error
    finally:
        if 'session' in locals() and session.is_active:
            session.close()

if __name__ == '__main__':
    seed_prepared_data()
