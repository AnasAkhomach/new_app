from sqlalchemy import inspect
from db_config import engine, Base
import logging
from models import *  # Import all models

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from db_config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, engine as default_engine # Renamed to avoid conflict

def setup_database():
    # Connect to MySQL server (without specifying a database initially)
    server_engine_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
    server_engine = create_engine(server_engine_url)

    try:
        with server_engine.connect() as connection:
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
            connection.commit() # Ensure the CREATE DATABASE command is committed
            logger.info(f"Database '{DB_NAME}' ensured to exist.")
    except OperationalError as e:
        logger.error(f"Could not connect to MySQL server or create database: {e}")
        return # Exit if database cannot be created or server not reachable
    except Exception as e:
        logger.error(f"An unexpected error occurred during database creation: {e}")
        return

    # Now connect to the specific database (engine from db_config.py should now work)
    # Re-assign engine to the one from db_config which points to the specific database
    # No, default_engine is already configured to the specific database. If it failed before, it was due to DB not existing.
    # We just need to ensure tables are created using this default_engine.
    try:
        inspector = inspect(default_engine) # Use the engine from db_config (now aliased)

        # Create all tables defined in the models if they don't exist
        if not inspector.get_table_names():
            logger.info("Creating database tables based on SQLAlchemy models...")
            Base.metadata.create_all(default_engine) # Use the engine from db_config
            logger.info("Database tables created successfully.")
        else:
            logger.info("Database tables already exist.")

        # Log the tables that were created
        # Refresh inspector for the specific database to get table names
        # The existing inspector was on default_engine which is already correct
        logger.info(f"Available tables in '{DB_NAME}': {inspector.get_table_names()}")

    except Exception as e:
        logger.error(f"Error setting up database: {e}")

def main():
    logger.info("Starting database setup...")
    setup_database()
    logger.info("Database setup completed.")

if __name__ == "__main__":
    main()
