from fastapi import FastAPI

from app.database import initialize_database, seed_database


app = FastAPI(
    title="Patient Appointment Agent"
)


@app.on_event("startup")
def startup():
    initialize_database()
    seed_database()


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Patient Appointment Agent is running"
    }