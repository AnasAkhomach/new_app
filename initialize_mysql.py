# initialize_mysql.py
import logging
from db_config import engine, Base
from models import *  # Ensure all models are imported to be registered with Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database_schema():
    logger.info("Initializing database schema...")
    try:
        Base.metadata.create_all(engine)
        logger.info("Database schema initialized successfully based on models.")
    except Exception as e:
        logger.error(f"Error initializing database schema: {e}")

if __name__ == "__main__":
    initialize_database_schema()