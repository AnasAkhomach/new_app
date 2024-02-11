from mongodb_transaction_manager import MongoDBClient
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_and_handle_duplicates_for_collection(db, collection_name, unique_field):
    """
    Find and handle duplicate documents in a specified collection.
    
    :param db: The database connection
    :param collection_name: The name of the collection to check for duplicates
    :param unique_field: The field that is supposed to be unique
    """
    duplicates = db[collection_name].aggregate([
        {"$group": {
            "_id": f"${unique_field}",
            "count": {"$sum": 1},
            "ids": {"$addToSet": "$_id"}
        }},
        {"$match": {
            "count": {"$gt": 1}
        }}
    ])

    for duplicate in duplicates:
        unique_value = duplicate["_id"]
        duplicate_ids = duplicate["ids"]
        logger.info(f"Duplicate found for {unique_field} {unique_value} with document IDs {duplicate_ids}")

        # Keep the first document ID and remove the rest
        to_keep = duplicate_ids.pop(0)
        logger.info(f"Keeping document with ID {to_keep} and removing the rest for {unique_field} {unique_value}")

        # Remove the duplicate documents
        db[collection_name].delete_many({"_id": {"$in": duplicate_ids}})
        logger.info(f"Removed duplicates: {duplicate_ids}")

def find_and_handle_all_duplicates(db):
    """
    Find and handle duplicates across all specified collections.
    
    :param db: The database connection
    """
    # Define a list of collections and their unique fields to check for duplicates
    collections_to_check = [
        {"name": "operating_rooms", "unique_field": "room_id"},
        {"name": "patients", "unique_field": "patient_id"},
        # Add more collections and their unique fields here
    ]

    for collection_info in collections_to_check:
        find_and_handle_duplicates_for_collection(db, collection_info["name"], collection_info["unique_field"])

def main():
    """
    Main function to execute the cleanup process.
    """
    db = MongoDBClient.get_db()  # Access the database using the MongoDBClient
    logger.info("Starting cleanup of duplicate entries across all collections...")
    find_and_handle_all_duplicates(db)
    logger.info("Cleanup completed.")

if __name__ == "__main__":
    main()
