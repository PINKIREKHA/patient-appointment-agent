
from app.database import initialize_database, seed_database

from app.tools.appointment_tools import (
    check_availability,
    book_appointment
)


def setup_module():
    initialize_database()
    seed_database()


def test_booking_requires_confirmation():

    result = book_appointment(
        doctor_name="Dr. Sharma",
        patient_name="Nancy",
        appointment_date="2026-10-20",
        appointment_time="11:00",
        confirmed=False
    )

    assert result["booked"] is False
    assert result["reason"] == "patient_confirmation_required"


def test_booking_with_confirmation():

    result = book_appointment(
        doctor_name="Dr. Sharma",
        patient_name="Test Patient",
        appointment_date="2026-11-15",
        appointment_time="11:00",
        confirmed=True
    )

    print("RESULT:", result)

    assert result["booked"] is True
    assert result["doctor"] == "Dr. Sharma"

