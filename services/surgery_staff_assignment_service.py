# surgery_staff_assignment_service.py

"""Service layer for managing surgery staff assignments in the surgical scheduling system."""

from sqlalchemy.exc import SQLAlchemyError
from models import SurgeryStaffAssignment


class SurgeryStaffAssignmentService:
    """Provides services for managing surgery staff assignments."""

    @staticmethod
    def create_surgery_staff_assignment(db, assignment_data):  # Added db parameter
        """Creates a new surgery staff assignment."""
        try:
            new_assignment = SurgeryStaffAssignment(
                surgery_id=assignment_data["surgery_id"],
                staff_id=assignment_data["staff_id"],
                role=assignment_data["role"],
            )
            db.add(new_assignment)
            db.commit()
            db.refresh(new_assignment)  # Kept db.refresh()
            print(
                f"Surgery staff assignment {new_assignment.assignment_id} created successfully."
            )
            return new_assignment.assignment_id
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error creating surgery staff assignment: {e}")
            return None

    @staticmethod
    def get_surgery_staff_assignment(db, assignment_id):  # Added db parameter
        """Fetches a surgery staff assignment by its ID."""
        try:
            assignment = (
                db.query(SurgeryStaffAssignment)
                .filter_by(assignment_id=assignment_id)
                .first()
            )
            if assignment:
                return assignment
            print("Surgery staff assignment not found.")
            return None
        except SQLAlchemyError as e:
            print(f"Error fetching surgery staff assignment: {e}")
            return None

    @staticmethod
    def update_surgery_staff_assignment(
        db, assignment_id, update_fields
    ):  # Added db parameter
        """Updates an existing surgery staff assignment."""
        try:
            result = (
                db.query(SurgeryStaffAssignment)
                .filter_by(assignment_id=assignment_id)
                .update(update_fields)
            )
            db.commit()
            if result:
                print(f"Surgery staff assignment {assignment_id} updated successfully.")
                return True
            print(f"No changes made to surgery staff assignment {assignment_id}.")
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error updating surgery staff assignment: {e}")
            return False

    @staticmethod
    def delete_surgery_staff_assignment(db, assignment_id):  # Added db parameter
        """Deletes a surgery staff assignment."""
        try:
            result = (
                db.query(SurgeryStaffAssignment)
                .filter_by(assignment_id=assignment_id)
                .delete()
            )
            db.commit()
            if result:
                print(f"Surgery staff assignment {assignment_id} deleted successfully.")
                return True
            print(f"Surgery staff assignment {assignment_id} not found.")
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error deleting surgery staff assignment: {e}")
            return False
