import pandas as pd
from sqlalchemy.orm import sessionmaker
from app.db.base import engine
from app.models.prepared_data import PreparedData
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def prepare_data():
    """
    This script pulls prepared data from the SQLite database and returns it as a pandas DataFrame.
    """
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        logging.info("SQLAlchemy session created for data retrieval.")

        logging.info("Loading prepared data from the database...")
        # Query all data from the PreparedData table
        data_from_db = session.query(PreparedData).all()

        # Convert list of SQLAlchemy objects to a list of dictionaries
        data_dicts = []
        for item in data_from_db:
            data_dicts.append({
                column.name: getattr(item, column.name)
                for column in item.__table__.columns
            })

        # Create a pandas DataFrame from the list of dictionaries
        df = pd.DataFrame(data_dicts)
        logging.info(f"Loaded {len(df)} rows from the database.")

        session.close()
        logging.info("SQLAlchemy session closed.")

        return df

    except Exception as e:
        logging.error(f"An error occurred during data retrieval from the database: {e}")
        return None

if __name__ == '__main__':
    # Example of how to use the function
    prepared_df = prepare_data()
    if prepared_df is not None:
        logging.info("Prepared DataFrame head:")
        logging.info(prepared_df.head())