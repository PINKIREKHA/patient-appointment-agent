# AI-Powered Patient Appointment Scheduling Agent

## Overview

This project is an AI-powered appointment scheduling agent built with Python, FastAPI, SQLite, and the OpenAI API. It helps patients check doctor availability, book appointments, and retrieve existing appointment details through a conversational interface.

The agent uses tools to interact with the database rather than relying on the language model to invent appointment information.

## Key Features

* **Doctor availability:** Checks whether a doctor exists and whether a requested appointment slot is available.
* **Appointment booking:** Books an appointment only after explicit patient confirmation.
* **Doctor validation:** Rejects booking requests for doctors who do not exist in the database.
* **Duplicate booking prevention:** Checks whether the requested doctor, date, and time slot is already booked.
* **Appointment lookup:** Retrieves appointment details from the database.
* **Persistent storage:** Uses SQLite to store doctor and appointment records.
* **REST API:** Exposes the agent through FastAPI.
* **Interactive API documentation:** Provides a Swagger UI for testing requests.
* **Automated tests:** Includes tests for booking behavior and safety scenarios.

## Technology Stack

* Python
* FastAPI
* OpenAI API
* SQLite
* Pytest
* Uvicorn

## Project Structure

```text
patient-appointment-agent/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── agent.py
│   ├── database.py
        validation.py
│   └── tools/
│       ├── __init__.py
│       └── appointment_tools.py
├── data/
│   └── clinic.db
eval
----evaluator.py
----improvement.py
----scenarios.py
├── tests/
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

*Note: The structure above is illustrative. Adjust it to match the actual files in your repository.*

## Prerequisites

* Python 3.11 or a compatible Python version supported by the installed dependencies.
* An OpenAI API key.
* Git, if cloning the repository.

## Installation and Setup

### 1. Clone the repository

Replace the placeholder URL with the public URL of your GitHub repository.

```bash
git clone https://github.com/PINKIREKHA/patient-appointment-agent.git
cd patient-appointment-agent
```

Alternatively, download the repository as a ZIP file and extract it.

### 2. Create a virtual environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Replace the placeholder with your own API key. Never commit your API key or other secrets to GitHub.

### 5. Initialize the database

Run the database initialization command or script provided by the project.

For example, if your project initializes the database through `app.database`, follow the initialization instructions in that module.

Ensure that the database contains the required doctor records before testing appointment booking.

## Running the Application

Start the FastAPI server from the project root:

```bash
uvicorn app.main:app --reload
```

Open the following URL in your browser:

* **Swagger UI:** http://127.0.0.1:8000/docs
* **API root:** http://127.0.0.1:8000/

Use Swagger UI to submit appointment requests and inspect the API responses.

## Testing

Run the automated test suite from the project root:

```bash
python -m pytest -v
```

### Important Scenarios to Test

1. **Successful booking:** A valid doctor, available slot, and explicit patient confirmation.
2. **Unknown doctor:** The booking request must be rejected if the doctor does not exist.
3. **Missing confirmation:** The appointment must not be booked without explicit confirmation.
4. **Already-booked slot:** A duplicate booking for the same doctor, date, and time must be rejected.
5. **Appointment lookup:** Existing appointment details should be returned from the database.

Example direct test of unknown-doctor validation:

```python
from app.tools.appointment_tools import book_appointment

result = book_appointment(
    doctor_name="Dr. Unknown",
    patient_name="Test Patient",
    appointment_date="2026-10-25",
    appointment_time="11:00",
    confirmed=True
)

assert result["booked"] is False
assert result["reason"] == "doctor_not_found"
```

## Safety and Reliability

The application implements database-backed doctor validation, availability checks, explicit confirmation before booking, and duplicate-slot checks.

The language model is responsible for understanding conversational requests, while the Python tools enforce booking rules against the database.

**Limitation:** The current implementation is a demonstration project. Production deployment would require additional protections, including authentication, authorization, input validation, secure handling of patient data, and concurrency-safe booking transactions.

## Future Improvements

* Add patient authentication and authorization.
* Add transaction-safe handling of simultaneous booking requests.
* Add appointment cancellation and rescheduling.
* Add structured logging and error monitoring.
* Add Docker-based deployment and CI/CD.
* Add stronger automated integration and safety tests.

## Author

Built as a practical project exploring AI agents, tool calling, database integration, API development, and reliable workflow automation.
