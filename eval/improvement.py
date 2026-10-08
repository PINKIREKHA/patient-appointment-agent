
FAILURE_IMPROVEMENTS = {
    "BOOKING_NOT_COMPLETED": {
        "category": "TOOL_SELECTION",
        "priority": "HIGH",
        "rule": (
            "When the patient explicitly confirms an appointment, "
            "the agent must attempt the booking operation instead "
            "of asking for confirmation again."
        ),
        "expected_behavior": (
            "After explicit confirmation, use the booking tool "
            "with the appointment details already collected."
        )
    },

    "UNSAFE_BOOKING": {
        "category": "SAFETY",
        "priority": "CRITICAL",
        "rule": (
            "Never create an appointment when the patient has "
            "not explicitly confirmed the appointment."
        ),
        "expected_behavior": (
            "Reject ambiguous confirmation and keep the "
            "appointment unbooked."
        )
    },

    "UNKNOWN_FAILURE": {
        "category": "GENERAL",
        "priority": "MEDIUM",
        "rule": (
            "Review the scenario and add a specific behavioral "
            "rule based on the observed failure."
        ),
        "expected_behavior": (
            "System behavior should match the expected "
            "scenario outcome."
        )
    }
}


def generate_improvement(failure_type):

    improvement = FAILURE_IMPROVEMENTS.get(
        failure_type
    )

    if improvement is None:

        return {
            "failure_type": failure_type,
            "category": "UNKNOWN",
            "priority": "LOW",
            "rule": "No predefined improvement available.",
            "expected_behavior": (
                "Manual review is required."
            )
        }

    return {
        "failure_type": failure_type,
        **improvement
    }


def generate_improvements(evaluation_results):

    improvements = []

    for result in evaluation_results:

        if result["passed"]:
            continue

        failure_type = result["failure_type"]

        improvement = generate_improvement(
            failure_type
        )

        improvements.append(
            {
                "scenario": result["name"],
                **improvement
            }
        )

    return improvements


def print_improvements(improvements):

    print()
    print("Structured Improvements")
    print("=======================")

    if not improvements:

        print("No failures detected.")
        return

    for improvement in improvements:

        print(
            f"Scenario: "
            f"{improvement['scenario']}"
        )

        print(
            f"Failure type: "
            f"{improvement['failure_type']}"
        )

        print(
            f"Category: "
            f"{improvement['category']}"
        )

        print(
            f"Priority: "
            f"{improvement['priority']}"
        )

        print(
            f"Rule: "
            f"{improvement['rule']}"
        )

        print(
            f"Expected behavior: "
            f"{improvement['expected_behavior']}"
        )

        print()

