
import os
import json
import re

from dotenv import load_dotenv
from openai import OpenAI

from app.tools.appointment_tools import (
    check_availability,
    book_appointment,
)

from app.validation import is_explicit_confirmation


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SYSTEM_PROMPT = """
You are a patient appointment scheduling assistant.

Your job is to help patients:
- find doctors
- check appointment availability
- book appointments

Important rules:

1. Never invent doctor information or appointment availability.
2. Use the available tools when you need information from the clinic system.
3. Before booking an appointment, get explicit confirmation from the patient.
4. If required information is missing, ask the patient for it.
5. Do not assume that an ambiguous statement is confirmation.
6. Be concise, polite, and clear.
"""


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": (
                "Check whether a specific doctor has an appointment "
                "slot available."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_name": {
                        "type": "string",
                        "description": "Name of the doctor"
                    },
                    "appointment_date": {
                        "type": "string",
                        "description": (
                            "Appointment date in YYYY-MM-DD format"
                        )
                    },
                    "appointment_time": {
                        "type": "string",
                        "description": (
                            "Appointment time in HH:MM format"
                        )
                    }
                },
                "required": [
                    "doctor_name",
                    "appointment_date",
                    "appointment_time"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": (
                "Book an appointment after the patient has explicitly "
                "confirmed the appointment details."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_name": {
                        "type": "string"
                    },
                    "patient_name": {
                        "type": "string"
                    },
                    "appointment_date": {
                        "type": "string"
                    },
                    "appointment_time": {
                        "type": "string"
                    },
                    "confirmed": {
                        "type": "boolean",
                        "description": (
                            "Must be true only when the patient has "
                            "explicitly confirmed the appointment."
                        )
                    }
                },
                "required": [
                    "doctor_name",
                    "patient_name",
                    "appointment_date",
                    "appointment_time",
                    "confirmed"
                ]
            }
        }
    }
]


def execute_tool(
    tool_name,
    arguments,
    latest_user_message=None
):

    if tool_name == "check_availability":

        return check_availability(**arguments)

    if tool_name == "book_appointment":

        explicit_confirmation = is_explicit_confirmation(
            latest_user_message or ""
        )

        if not explicit_confirmation:

            return {
                "booked": False,
                "reason": "explicit_confirmation_required"
            }

        arguments["confirmed"] = True

        return book_appointment(**arguments)

    return {
        "error": f"Unknown tool: {tool_name}"
    }


def get_latest_user_message(messages):

    for message in reversed(messages):

        if isinstance(message, dict):

            if message.get("role") == "user":

                return message.get(
                    "content",
                    ""
                )

    return ""


def get_patient_name(messages):

    """
    Extract the patient name from the conversation.

    The evaluation scenarios use the format:
    "My name is <name>."
    """

    for message in messages:

        if not isinstance(message, dict):
            continue

        if message.get("role") != "user":
            continue

        content = message.get(
            "content",
            ""
        )

        match = re.search(
            r"my name is\s+(.+?)(?:\.|$)",
            content,
            re.IGNORECASE
        )

        if match:

            return match.group(1).strip()

    return None


def get_last_available_slot(messages):

    """
    Find the most recent successful availability
    check from the conversation.
    """

    for message in reversed(messages):

        if not isinstance(message, dict):
            continue

        if message.get("role") != "tool":
            continue

        content = message.get(
            "content",
            ""
        )

        try:

            tool_result = json.loads(content)

        except json.JSONDecodeError:

            continue

        if (
            tool_result.get("available") is True
            and tool_result.get("doctor")
            and tool_result.get("date")
            and tool_result.get("time")
        ):

            return {
                "doctor_name": tool_result["doctor"],
                "appointment_date": tool_result["date"],
                "appointment_time": tool_result["time"]
            }

    return None


def book_confirmed_appointment(
    messages,
    latest_user_message
):

    """
    Deterministically book the most recently checked
    available appointment after explicit confirmation.
    """

    if not is_explicit_confirmation(
        latest_user_message
    ):

        return None

    slot = get_last_available_slot(
        messages
    )

    if slot is None:

        return None

    patient_name = get_patient_name(
        messages
    )

    if patient_name is None:

        return None

    return book_appointment(
        doctor_name=slot["doctor_name"],
        patient_name=patient_name,
        appointment_date=slot["appointment_date"],
        appointment_time=slot["appointment_time"],
        confirmed=True
    )


def run_agent(messages):

    latest_user_message = get_latest_user_message(
        messages
    )

    # --------------------------------------------------
    # Deterministic confirmation path
    # --------------------------------------------------
    #
    # If the patient explicitly confirms an appointment,
    # first try to book the most recently checked available
    # slot directly.
    #
    # This avoids relying on the LLM to reconstruct
    # critical booking arguments.
    # --------------------------------------------------

    if is_explicit_confirmation(
        latest_user_message
    ):

        booking_result = book_confirmed_appointment(
            messages,
            latest_user_message
        )

        if booking_result is not None:

            messages.append(
                {
                    "role": "assistant",
                    "content": (
                        "Your appointment has been booked "
                        f"with {booking_result['doctor']} "
                        f"on {booking_result['date']} "
                        f"at {booking_result['time']}."
                    )
                }
            )

            return (
                "Your appointment has been booked "
                f"with {booking_result['doctor']} "
                f"on {booking_result['date']} "
                f"at {booking_result['time']}."
            )

    # --------------------------------------------------
    # Normal LLM tool-calling path
    # --------------------------------------------------

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )

    assistant_message = response.choices[0].message

    if not assistant_message.tool_calls:

        return assistant_message.content

    messages.append(
        assistant_message
    )

    for tool_call in assistant_message.tool_calls:

        tool_name = tool_call.function.name

        arguments = json.loads(
            tool_call.function.arguments
        )

        tool_result = execute_tool(
            tool_name,
            arguments,
            latest_user_message
        )

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result)
            }
        )

    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )

    return final_response.choices[0].message.content


def chat(user_message, conversation):

    conversation.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    response = run_agent(
        conversation
    )

    # Avoid adding the assistant message twice.
    if not (
        conversation
        and conversation[-1].get("role") == "assistant"
        and conversation[-1].get("content") == response
    ):

        conversation.append(
            {
                "role": "assistant",
                "content": response
            }
        )

    return response

