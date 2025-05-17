import sys
import os

# Adjust the path to ensure shared modules can be found if necessary
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Removed MongoDBClient import


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

        for surgery in surgeries_data:  # Assumes surgery is a dict or object
            if not isinstance(surgery, dict):
                continue  # Skip None or invalid types
            surgeon_id = surgery.get("surgeon_id")
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

            for preference_key, expected_value in preferences.items():
                actual_value = surgery.get(preference_key)
                total_preferences_checked += 1
                if actual_value == expected_value:
                    satisfied_preferences_count += 1

        satisfaction_score = (
            (satisfied_preferences_count / total_preferences_checked) * 100
            if total_preferences_checked > 0
            else 0
        )
        return satisfaction_score

    def get_surgeon_preferences(self, surgeon_id):
        # This method needs to be implemented to fetch surgeon preferences using SQLAlchemy
        if self.db_session:
            # Example: preference_model = self.db_session.query(SurgeonPreferenceModel).filter_by(surgeon_id=surgeon_id).first()
            # return preference_model.preferences if preference_model else {}
            print(
                f"Fetching preferences for surgeon {surgeon_id} via db_session needs implementation."
            )
            return {}  # Placeholder
        print(f"Cannot fetch preferences for surgeon {surgeon_id}: no db_session.")
        return {}  # Placeholder


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
