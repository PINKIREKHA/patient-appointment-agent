from app.database import get_connection


def check_availability(
    doctor_name: str,
    appointment_date: str,
    appointment_time: str
):
    connection = get_connection()
    cursor = connection.cursor()

    # Find the doctor
    cursor.execute(
        """
        SELECT id, name, specialty
        FROM doctors
        WHERE LOWER(name) = LOWER(?)
        """,
        (doctor_name,)
    )

    doctor = cursor.fetchone()

    if doctor is None:
        connection.close()

        return {
            "available": False,
            "reason": "doctor_not_found"
        }

    # Check whether the requested slot is already booked
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

    connection.close()

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

def book_appointment(
    doctor_name: str,
    patient_name: str,
    appointment_date: str,
    appointment_time: str,
    confirmed: bool
):
    if not confirmed:
        return {
            "booked": False,
            "reason": "patient_confirmation_required"
        }

    connection = get_connection()
    cursor = connection.cursor()

    # Find the doctor
    cursor.execute(
        """
        SELECT id, name, specialty
        FROM doctors
        WHERE LOWER(name) = LOWER(?)
        """,
        (doctor_name,)
    )

    doctor = cursor.fetchone()

    if doctor is None:
        connection.close()

        return {
            "booked": False,
            "reason": "doctor_not_found"
        }

    # Check whether the slot is already booked
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
        connection.close()

        return {
            "booked": False,
            "reason": "slot_already_booked"
        }

    # Create the appointment
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
    connection.close()

    return {
        "booked": True,
        "appointment_id": appointment_id,
        "doctor": doctor["name"],
        "specialty": doctor["specialty"],
        "patient": patient_name,
        "date": appointment_date,
        "time": appointment_time
    }

def get_appointment(
    doctor_name: str,
    patient_name: str,
    appointment_date: str,
    appointment_time: str
):
    connection = get_connection()
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
        WHERE LOWER(doctors.name) = LOWER(?)
          AND LOWER(appointments.patient_name) = LOWER(?)
          AND appointments.appointment_date = ?
          AND appointments.appointment_time = ?
        """,
        (
            doctor_name,
            patient_name,
            appointment_date,
            appointment_time
        )
    )

    appointment = cursor.fetchone()

    connection.close()

    if appointment is None:
        return None

    return dict(appointment)