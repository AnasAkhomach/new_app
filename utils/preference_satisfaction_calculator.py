import sys
import os

# Adjust the path to ensure the mongodb_transaction_manager is found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mongodb_transaction_manager import MongoDBClient

class PreferenceSatisfactionCalculator:
    def __init__(self):
        # Initialize MongoDB client
        self.db = MongoDBClient.get_db()

    def calculate(self, surgeries):
        # Initialize counters for preferences
        total_preferences = 0
        satisfied_preferences = 0
        
        # Iterate over each surgery to compare against surgeon preferences
        for surgery in surgeries:
            surgeon_id = surgery.get('surgeon_id')
            preferences = self.get_surgeon_preferences(surgeon_id)
            
            # Iterate through each preference to check if it's satisfied
            for preference_key, expected_value in preferences.items():
                actual_value = surgery.get(preference_key)  # Get the corresponding value from the surgery
                total_preferences += 1  # Count each preference check
                if actual_value == expected_value:
                    satisfied_preferences += 1  # Count if the preference is satisfied

        # Calculate and return the preference satisfaction score
        satisfaction_score = satisfied_preferences / total_preferences if total_preferences else 0
        return satisfaction_score

    def get_surgeon_preferences(self, surgeon_id):
        # Fetch surgeon preferences from the database
        try:
            preferences_document = self.db.surgeon_preferences.find_one({"surgeon_id": surgeon_id})
            # Return preferences if found, else return an empty dict
            return preferences_document.get('preferences', {}) if preferences_document else {}
        except Exception as e:
            print(f"Error fetching preferences for surgeon {surgeon_id}: {e}")
            return {}

# Note: The `calculate_preference_satisfaction` method was integrated into the `calculate` method for simplicity.
# The `is_preference_satisfied` method was not needed as the preference satisfaction check is directly performed in the loop.
