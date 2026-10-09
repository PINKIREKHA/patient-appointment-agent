
from app.database import get_connection


def check_availability(
    doctor_name: str,
    appointment_date: str,
    appointment_time: str
):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, name, specialty
            FROM doctors
            WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
            """,
            (doctor_name.strip(),)
        )

        doctor = cursor.fetchone()

        if doctor is None:
            return {
                "available": False,
                "reason": "doctor_not_found",
                "message": (
                    f"Doctor '{doctor_name}' does not exist "
                    "in the database."
                )
            }

        cursor.execute(
            """
            SELECT id
            FROM appointments
            WHERE doctor_id = ?
              AND appointment_date = ?
              AND appointment_time = ?
              AND status = 'booked'
            """,
            (
                doctor["id"],
                appointment_date,
                appointment_time
            )
        )

        appointment = cursor.fetchone()

        if appointment is not None:
            return {
                "available": False,
                "reason": "slot_already_booked",
                "doctor": doctor["name"],
                "date": appointment_date,
                "time": appointment_time
            }

        return {
            "available": True,
            "doctor": doctor["name"],
            "specialty": doctor["specialty"],
            "date": appointment_date,
            "time": appointment_time
        }

    finally:
        connection.close()


def book_appointment(
    doctor_name: str,
    patient_name: str,
    appointment_date: str,
    appointment_time: str,
    confirmed: bool
):
    if confirmed is not True:
        return {
            "booked": False,
            "reason": "patient_confirmation_required",
            "message": "Explicit patient confirmation is required."
        }

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Step 1: Verify the doctor exists.
        cursor.execute(
            """
            SELECT id, name, specialty
            FROM doctors
            WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
            """,
            (doctor_name.strip(),)
        )

        doctor = cursor.fetchone()

        if doctor is None:
            return {
                "booked": False,
                "reason": "doctor_not_found",
                "message": (
                    f"Doctor '{doctor_name}' does not exist. "
                    "No appointment was booked."
                )
            }

        # Step 2: Check that the requested slot is available.
        cursor.execute(
            """
            SELECT id
            FROM appointments
            WHERE doctor_id = ?
              AND appointment_date = ?
              AND appointment_time = ?
              AND status = 'booked'
            """,
            (
                doctor["id"],
                appointment_date,
                appointment_time
            )
        )

        existing_appointment = cursor.fetchone()

        if existing_appointment is not None:
            return {
                "booked": False,
                "reason": "slot_already_booked",
                "message": "This time slot is already booked."
            }

        # Step 3: Create the appointment.
        cursor.execute(
            """
            INSERT INTO appointments (
                doctor_id,
                patient_name,
                appointment_date,
                appointment_time,
                status
            )
            VALUES (?, ?, ?, ?, 'booked')
            """,
            (
                doctor["id"],
                patient_name,
                appointment_date,
                appointment_time
            )
        )

        appointment_id = cursor.lastrowid
        connection.commit()

        return {
            "booked": True,
            "appointment_id": appointment_id,
            "doctor": doctor["name"],
            "specialty": doctor["specialty"],
            "patient": patient_name,
            "date": appointment_date,
            "time": appointment_time,
            "message": "Appointment booked successfully."
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_appointment(
    doctor_name: str,
    patient_name: str,
    appointment_date: str,
    appointment_time: str
):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                appointments.id,
                doctors.name AS doctor,
                appointments.patient_name,
                appointments.appointment_date,
                appointments.appointment_time,
                appointments.status
            FROM appointments
            JOIN doctors
                ON appointments.doctor_id = doctors.id
            WHERE LOWER(TRIM(doctors.name)) = LOWER(TRIM(?))
              AND LOWER(TRIM(appointments.patient_name))
                  = LOWER(TRIM(?))
              AND appointments.appointment_date = ?
              AND appointments.appointment_time = ?
            """,
            (
                doctor_name.strip(),
                patient_name.strip(),
                appointment_date,
                appointment_time
            )
        )

        appointment = cursor.fetchone()

        if appointment is None:
            return None

        return dict(appointment)

    finally:
        connection.close()