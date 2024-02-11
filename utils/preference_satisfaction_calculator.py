# utils/preference_satisfaction_calculator.py
from mongodb_transaction_manager import MongoDBClient

class PreferenceSatisfactionCalculator:
    #I WILL STOP HERE FOR TODAY:
    def __init__(self):
        self.db = MongoDBClient.get_db()

    def calculate(self, surgeries):
        total_preferences = 0
        satisfied_preferences = 0
        
        for surgery in surgeries:
            surgeon_id = surgery['surgeon_id']
            preferences = self.get_surgeon_preferences(surgeon_id)
            
            # Assuming the surgery document and surgeon preferences are structured to allow comparison
            # Example: Check if surgery type matches surgeon's preferred type
            if 'type' in preferences and 'surgery_type' in surgery:
                total_preferences += 1  # Every preference checked is counted
                if surgery['surgery_type'] == preferences['type']:
                    satisfied_preferences += 1

            # Extend logic for other preferences like preferred equipment, time slots, etc.

        # Calculate satisfaction score
        satisfaction_score = satisfied_preferences / total_preferences if total_preferences > 0 else 0
        return satisfaction_score

    def get_surgeon_preferences(self, surgeon_id):
        try:
            preferences_document = self.db.surgeon_preferences.find_one({"surgeon_id": surgeon_id})
            return preferences_document.get('preferences', {}) if preferences_document else {}
        except Exception as e:
            print(f"Error fetching preferences for surgeon {surgeon_id}: {e}")
            return {}
