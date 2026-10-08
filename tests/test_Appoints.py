from app.database import initialize_database, seed_database
from app.tools.appointment_tools import check_availability


def setup_module():
    initialize_database()
    seed_database()


def test_doctor_available():
    result = check_availability(
        doctor_name="Dr. Sharma",
        appointment_date="2026-10-13",
        appointment_time="15:00"
    )

    assert result["available"] is True


def test_unknown_doctor():
    result = check_availability(
        doctor_name="Dr. Unknown",
        appointment_date="2026-10-13",
        appointment_time="15:00"
    )

    assert result["available"] is False
    assert result["reason"] == "doctor_not_found"