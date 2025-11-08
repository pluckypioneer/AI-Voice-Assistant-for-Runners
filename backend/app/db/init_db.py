import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.db.base import Base, engine
    # Import models to ensure they are registered with the Base
    from app.models.user import User
    from app.models.fitness_data import FitnessData
    
    def init_db():
        """Initialize the database and create all tables."""
        print("Starting database initialization...")
        print(f"Database URL: {engine.url}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")

    if __name__ == "__main__":
        init_db()
        
except Exception as e:
    print(f"Error during database initialization: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)