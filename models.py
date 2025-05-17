from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Enum as GenericEnum,  # Changed from MySQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class OperatingRoom(Base):
    __tablename__ = "operatingroom"
    room_id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(255), nullable=False)
    surgeries = relationship("Surgery", back_populates="room")
    equipment = relationship("OperatingRoomEquipment", back_populates="room")


class Patient(Base):
    __tablename__ = "patient"
    patient_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    dob = Column(Date, nullable=False)
    contact_info = Column(String(255), nullable=True)
    privacy_consent = Column(Boolean, nullable=False, server_default="0")
    surgeries = relationship("Surgery", back_populates="patient")
    appointments = relationship("SurgeryAppointment", back_populates="patient")
    medical_history = relationship("PatientMedicalHistory", back_populates="patient")


class Staff(Base):
    __tablename__ = "staff"
    staff_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)
    contact_info = Column(String(255), nullable=True)
    specialization = Column(String(255), nullable=True)
    availability = Column(Boolean, nullable=False, server_default="1")
    assignments = relationship("SurgeryStaffAssignment", back_populates="staff")


class Surgeon(Base):
    __tablename__ = "surgeon"
    surgeon_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    contact_info = Column(String(255), nullable=True)
    specialization = Column(String(255), nullable=False)
    credentials = Column(Text, nullable=False)
    availability = Column(Boolean, nullable=False, server_default="1")
    surgeries = relationship("Surgery", back_populates="surgeon")
    appointments = relationship("SurgeryAppointment", back_populates="surgeon")
    preferences = relationship("SurgeonPreference", back_populates="surgeon")


class SurgeryEquipment(Base):
    __tablename__ = "surgeryequipment"
    equipment_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)
    availability = Column(Boolean, nullable=False, server_default="1")
    usages = relationship("SurgeryEquipmentUsage", back_populates="equipment")


class Surgery(Base):
    __tablename__ = "surgery"
    surgery_id = Column(Integer, primary_key=True, autoincrement=True)
    scheduled_date = Column(DateTime, nullable=False)
    surgery_type = Column(String(100), nullable=False)
    # Changed MySQLEnum to GenericEnum with native_enum=False
    urgency_level = Column(
        GenericEnum(
            "Low", "Medium", "High", name="urgency_level_enum", native_enum=False
        ),
        nullable=False,
    )
    duration_minutes = Column(Integer, nullable=False)
    # Changed MySQLEnum to GenericEnum with native_enum=False
    status = Column(
        GenericEnum(
            "Scheduled",
            "In Progress",
            "Completed",
            "Cancelled",
            name="surgery_status_enum",
            native_enum=False,
        ),
        nullable=False,
        server_default="Scheduled",
    )
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    patient_id = Column(
        Integer,
        ForeignKey("patient.patient_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
    )
    surgeon_id = Column(
        Integer,
        ForeignKey("surgeon.surgeon_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
    )
    room_id = Column(
        Integer,
        ForeignKey("operatingroom.room_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
    )
    patient = relationship("Patient", back_populates="surgeries")
    surgeon = relationship("Surgeon", back_populates="surgeries")
    room = relationship("OperatingRoom", back_populates="surgeries")
    equipment_usages = relationship("SurgeryEquipmentUsage", back_populates="surgery")
    staff_assignments = relationship("SurgeryStaffAssignment", back_populates="surgery")


class OperatingRoomEquipment(Base):
    __tablename__ = "operatingroomequipment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(
        Integer,
        ForeignKey("operatingroom.room_id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    equipment_name = Column(String(255), nullable=False)
    room = relationship("OperatingRoom", back_populates="equipment")


class PatientMedicalHistory(Base):
    __tablename__ = "patientmedicalhistory"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(
        Integer,
        ForeignKey("patient.patient_id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    medical_condition = Column(String(255), nullable=False)
    diagnosis_date = Column(Date, nullable=False)
    patient = relationship("Patient", back_populates="medical_history")


class SurgeryEquipmentUsage(Base):
    __tablename__ = "surgeryequipmentusage"
    usage_id = Column(Integer, primary_key=True, autoincrement=True)
    surgery_id = Column(
        Integer,
        ForeignKey("surgery.surgery_id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    equipment_id = Column(
        Integer,
        ForeignKey(
            "surgeryequipment.equipment_id", ondelete="RESTRICT", onupdate="CASCADE"
        ),
    )
    usage_start_time = Column(DateTime, nullable=True)  # Added this line
    usage_end_time = Column(DateTime, nullable=True)  # Added this line
    surgery = relationship("Surgery", back_populates="equipment_usages")
    equipment = relationship("SurgeryEquipment", back_populates="usages")


class SurgeryStaffAssignment(Base):
    __tablename__ = "surgerystaffassignment"
    assignment_id = Column(Integer, primary_key=True, autoincrement=True)
    surgery_id = Column(
        Integer,
        ForeignKey("surgery.surgery_id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    staff_id = Column(
        Integer, ForeignKey("staff.staff_id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    role = Column(String(100), nullable=False)
    surgery = relationship("Surgery", back_populates="staff_assignments")
    staff = relationship("Staff", back_populates="assignments")


class SurgeryAppointment(Base):
    __tablename__ = "surgeryappointment"
    appointment_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(
        Integer,
        ForeignKey("patient.patient_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    surgeon_id = Column(
        Integer,
        ForeignKey("surgeon.surgeon_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    room_id = Column(
        Integer,
        ForeignKey("operatingroom.room_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    appointment_date = Column(DateTime, nullable=False)
    # Changed MySQLEnum to GenericEnum with native_enum=False
    status = Column(
        GenericEnum(
            "Scheduled",
            "Completed",
            "Cancelled",
            name="appointment_status_enum",
            native_enum=False,
        ),
        nullable=False,
        server_default="Scheduled",
    )
    notes = Column(Text, nullable=True)
    patient = relationship("Patient", back_populates="appointments")
    surgeon = relationship("Surgeon", back_populates="appointments")
    room = relationship("OperatingRoom")


class SurgeonPreference(Base):
    __tablename__ = "surgeonpreference"
    preference_id = Column(Integer, primary_key=True, autoincrement=True)
    surgeon_id = Column(
        Integer,
        ForeignKey("surgeon.surgeon_id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    preference_type = Column(String(100), nullable=False)
    preference_value = Column(String(255), nullable=False)
    surgeon = relationship("Surgeon", back_populates="preferences")


class SurgeryRoomAssignment(Base):
    __tablename__ = "surgeryroomassignment"
    assignment_id = Column(Integer, primary_key=True, autoincrement=True)
    surgery_id = Column(
        Integer,
        ForeignKey("surgery.surgery_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    room_id = Column(
        Integer,
        ForeignKey("operatingroom.room_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
