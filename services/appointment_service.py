"""Service layer for managing surgery appointments in the surgical scheduling system."""

from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from models import SurgeryAppointment


class AppointmentService:
    """Provides services for managing surgery appointments."""

    @staticmethod
    def create_surgery_appointment(db, appointment_data):  # Added db parameter
        """Creates a new surgery appointment."""
        try:
            # Convert appointment_date to datetime if present as string
            if "appointment_date" in appointment_data and isinstance(
                appointment_data["appointment_date"], str
            ):
                appointment_data["appointment_date"] = datetime.fromisoformat(
                    appointment_data["appointment_date"]
                )

            new_appointment = SurgeryAppointment(
                patient_id=appointment_data["patient_id"],
                surgeon_id=appointment_data["surgeon_id"],
                room_id=appointment_data["room_id"],
                appointment_date=appointment_data["appointment_date"],
                status=appointment_data.get("status", "Scheduled"),
                notes=appointment_data.get("notes"),
            )
            db.add(new_appointment)
            db.commit()
            db.refresh(new_appointment)  # Kept db.refresh()
            print(
                f"Surgery appointment {new_appointment.appointment_id} created successfully."
            )
            return new_appointment.appointment_id
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error creating surgery appointment: {e}")
            return None

    @staticmethod
    def get_appointment(db, appointment_id):  # Added db parameter
        """Fetches a surgery appointment by its ID."""
        try:
            appointment = (
                db.query(SurgeryAppointment)
                .filter_by(appointment_id=appointment_id)
                .first()
            )
            if appointment:
                return appointment
            print("Surgery appointment not found.")
            return None
        except SQLAlchemyError as e:
            print(f"Error fetching surgery appointment: {e}")
            return None

    @staticmethod
    def update_appointment(db, appointment_id, update_fields):  # Added db parameter
        """Updates an existing surgery appointment."""
        try:
            # Convert appointment_date to datetime if present as string
            if "appointment_date" in update_fields and isinstance(
                update_fields["appointment_date"], str
            ):
                update_fields["appointment_date"] = datetime.fromisoformat(
                    update_fields["appointment_date"]
                )

            result = (
                db.query(SurgeryAppointment)
                .filter_by(appointment_id=appointment_id)
                .update(update_fields)
            )
            db.commit()
            if result:
                print(f"Surgery appointment {appointment_id} updated successfully.")
                return True
            print(f"No changes made to surgery appointment {appointment_id}.")
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error updating surgery appointment: {e}")
            return False

    @staticmethod
    def delete_appointment(db, appointment_id):  # Added db parameter
        """Deletes a surgery appointment."""
        try:
            result = (
                db.query(SurgeryAppointment)
                .filter_by(appointment_id=appointment_id)
                .delete()
            )
            db.commit()
            if result:
                print(f"Surgery appointment {appointment_id} deleted successfully.")
                return True
            print(f"Surgery appointment {appointment_id} not found.")
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error deleting surgery appointment: {e}")
            return False

    # Note: Validation methods (is_room_available, is_staff_available) need to be reimplemented
    # using SQLAlchemy queries if they are still required for business logic.
    # The current implementation relies on MongoDB specific queries.


# Example usage (optional)
if __name__ == "__main__":
    # This example usage will now require a db session to be passed.
    pass
