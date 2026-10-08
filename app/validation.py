
import re


def is_explicit_confirmation(message: str) -> bool:
    """
    Check whether the patient's message is an explicit
    confirmation to proceed with booking.
    """

    normalized_message = message.strip().lower()

    # Remove punctuation so that:
    # "Yes, please book it."
    # becomes:
    # "yes please book it"
    normalized_message = re.sub(
        r"[^\w\s]",
        "",
        normalized_message
    )

    normalized_message = re.sub(
        r"\s+",
        " ",
        normalized_message
    ).strip()

    confirmation_phrases = {
        "yes",
        "yes please",
        "please book it",
        "book it",
        "book this",
        "confirm",
        "confirmed",
        "go ahead",
        "yes book it",
        "yes please book it",
        "yes go ahead",
        "please confirm",
    }

    return normalized_message in confirmation_phrases

