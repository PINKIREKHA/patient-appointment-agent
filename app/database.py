import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/clinic.db")


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER NOT NULL,
            patient_name TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'booked',

            FOREIGN KEY (doctor_id)
                REFERENCES doctors(id)
        )
    """)

    connection.commit()
    connection.close()


def seed_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM doctors")
    doctor_count = cursor.fetchone()[0]

    if doctor_count == 0:
        doctors = [
            ("Dr. Sharma", "Cardiology"),
            ("Dr. Mehta", "Dermatology"),
            ("Dr. Patel", "General Medicine"),
        ]

        cursor.executemany(
            """
            INSERT INTO doctors (name, specialty)
            VALUES (?, ?)
            """,
            doctors
        )

    connection.commit()
    connection.close()