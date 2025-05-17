import sys
import os
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from db_config import engine

def test_connection():
    try:
        # Try to connect and execute a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Successfully connected to the database!")

            # Check if our database exists
            db_result = connection.execute(text("SHOW DATABASES LIKE 'surgery_scheduler'"))
            if db_result.rowcount > 0:
                print("✅ The 'surgery_scheduler' database exists!")
            else:
                print("❌ The 'surgery_scheduler' database does not exist yet.")

            # Check if any tables exist in our database
            try:
                connection.execute(text("USE surgery_scheduler"))
                table_result = connection.execute(text("SHOW TABLES"))
                tables = table_result.fetchall()

                if tables:
                    print(f"✅ Found {len(tables)} tables in the database:")
                    for table in tables:
                        print(f"  - {table[0]}")
                else:
                    print("⚠️ No tables found in the database yet.")
            except SQLAlchemyError as e:
                print(f"❌ Error checking tables: {e}")

    except SQLAlchemyError as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    print("Testing connection to MySQL database...")
    test_connection()