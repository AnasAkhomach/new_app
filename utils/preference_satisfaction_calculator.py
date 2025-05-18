import sys
import os

# Adjust the path to ensure shared modules can be found if necessary
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models import SurgeonPreference # Import the SurgeonPreference model


class PreferenceSatisfactionCalculator:
    def __init__(self, db_session=None):
        # Accept a database session (e.g., SQLAlchemy session) for potential MySQL integration
        self.db_session = db_session

    def calculate(self, surgeries_data, surgeon_preferences_map=None):
        # surgeries_data: list of dicts/objects representing surgeries
        # surgeon_preferences_map: dict mapping surgeon_id to their preferences dict
        # If surgeon_preferences_map is None, it will try to fetch using get_surgeon_preferences

        if not surgeries_data:
            return 0  # No surgeries, so no preferences to satisfy or violate

        total_preferences_checked = 0
        satisfied_preferences_count = 0

        for surgery_assignment in surgeries_data:  # Expecting SurgeryRoomAssignment objects
            if not hasattr(surgery_assignment, 'surgery') or not surgery_assignment.surgery:
                continue

            surgery = surgery_assignment.surgery
            surgeon_id = surgery.surgeon_id
            if not surgeon_id:
                continue  # Skip if no surgeon is assigned

            if surgeon_preferences_map and surgeon_id in surgeon_preferences_map:
                preferences = surgeon_preferences_map[surgeon_id]
            elif self.db_session:  # Fallback to fetching if db_session is available
                preferences = self.get_surgeon_preferences(surgeon_id)
            else:  # No preferences available for this surgeon
                preferences = {}

            if not preferences:  # No preferences defined for this surgeon
                continue

            # Extract relevant details from surgery_assignment for preference checking
            # This needs to align with how preferences are stored and what surgery_assignment provides
            # Example: day_of_week, room_id (or room_type), time_of_day
            actual_day_of_week = surgery_assignment.start_time.strftime("%A") if surgery_assignment.start_time else None
            actual_room_id = surgery_assignment.room.room_id if surgery_assignment.room else None
            # Add more actual values as needed based on preference types

            for preference_key, expected_value in preferences.items():
                actual_value = None
                if preference_key == "day_of_week":
                    actual_value = actual_day_of_week
                elif preference_key == "room_id": # Assuming preference might be for a specific room_id
                    actual_value = actual_room_id
                elif preference_key == "room_location": # Example: if preference is for room location
                    actual_value = surgery_assignment.room.location if surgery_assignment.room else None
                # Add more mappings from preference_key to actual_value from surgery_assignment

                if actual_value is not None: # Only check if we have an actual value to compare
                    total_preferences_checked += 1
                    if str(actual_value) == str(expected_value): # Ensure type consistency for comparison
                        satisfied_preferences_count += 1

        satisfaction_score = (
            (satisfied_preferences_count / total_preferences_checked) * 100
            if total_preferences_checked > 0
            else 100 # If no preferences to check, consider it 100% satisfied or 0 based on desired behavior
        )
        return satisfaction_score

    def get_surgeon_preferences(self, surgeon_id):
        if self.db_session:
            preferences_db = self.db_session.query(SurgeonPreference).filter_by(surgeon_id=surgeon_id).all()
            if not preferences_db:
                # print(f"No preferences found for surgeon {surgeon_id}.")
                return {}

            # Convert list of preference objects to a dictionary
            # Example: {'day_of_week': 'Monday', 'preferred_room_type': 'A'}
            surgeon_prefs_dict = {}
            for pref in preferences_db:
                # Assuming SurgeonPreference has 'preference_type' and 'preference_value' columns
                # Adjust key names if your model uses different attribute names
                if hasattr(pref, 'preference_type') and hasattr(pref, 'preference_value'):
                    surgeon_prefs_dict[pref.preference_type] = pref.preference_value
                else:
                    print(f"Warning: Preference object for surgeon {surgeon_id} lacks 'preference_type' or 'preference_value'.")
            # print(f"Fetched preferences for surgeon {surgeon_id}: {surgeon_prefs_dict}")
            return surgeon_prefs_dict

        print(f"Cannot fetch preferences for surgeon {surgeon_id}: no db_session provided.")
        return {} # Fallback if no db_session


# Example Usage
if __name__ == "__main__":
    # calculator = PreferenceSatisfactionCalculator(db_session=your_sqla_session)
    calculator = PreferenceSatisfactionCalculator()

    mock_surgeries = [
        {
            "surgery_id": "s1",
            "surgeon_id": "dr_A",
            "room_id": "OR1",
            "day_of_week": "Monday",
        },
        {
            "surgery_id": "s2",
            "surgeon_id": "dr_B",
            "room_id": "OR2",
            "day_of_week": "Tuesday",
        },
        {
            "surgery_id": "s3",
            "surgeon_id": "dr_A",
            "room_id": "OR1",
            "day_of_week": "Wednesday",
        },  # dr_A prefers Monday
    ]

    # Option 1: Provide preferences directly
    mock_preferences_map = {
        "dr_A": {"day_of_week": "Monday", "room_id": "OR1"},
        "dr_B": {"day_of_week": "Tuesday"},
    }
    score_with_map = calculator.calculate(
        mock_surgeries, surgeon_preferences_map=mock_preferences_map
    )
    print(f"Preference Satisfaction Score (with map): {score_with_map:.2f}%")

    # Option 2: Rely on get_surgeon_preferences (requires db_session and implementation)
    # This will print placeholder messages if get_surgeon_preferences is not fully implemented.
    # To test this path, you would instantiate calculator with a db_session and ensure
    # get_surgeon_preferences can fetch data.
    # score_via_method = calculator.calculate(mock_surgeries)
    # print(f"Preference Satisfaction Score (via method): {score_via_method:.2f}%")
