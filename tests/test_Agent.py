from app.agent import run_agent


def test_agent_can_answer():

    messages = [
        {
            "role": "system",
            "content": """
            You are a patient appointment scheduling assistant.

            Help patients find doctors, check availability,
            and book appointments.

            Never book an appointment without explicit
            patient confirmation.
            """
        },
        {
            "role": "user",
            "content": "Is Dr. Sharma available on 2026-10-20 at 15:00?"
        }
    ]

    response = run_agent(messages)

    assert response is not None
    assert len(response) > 0