from app.agent import chat


def test_multi_turn_conversation():

    conversation = [
        {
            "role": "system",
            "content": """
            You are a patient appointment scheduling assistant.

            Help patients find doctors, check availability,
            and book appointments.

            Never book an appointment without explicit
            patient confirmation.
            """
        }
    ]

    response1 = chat(
        "I want to see Dr. Sharma.",
        conversation
    )

    assert response1 is not None

    response2 = chat(
        "October 20, 2026.",
        conversation
    )

    assert response2 is not None

    response3 = chat(
        "11 AM.",
        conversation
    )

    assert response3 is not None

    response4 = chat(
        "Yes, please book it.",
        conversation
    )

    assert response4 is not None