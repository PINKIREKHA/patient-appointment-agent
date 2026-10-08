# Design Note — Patient Appointment Scheduling Agent

## 1. Problem

The goal of this project is to build an AI agent that helps patients schedule doctor appointments through a natural multi-turn conversation.

The agent should collect the required appointment information, check doctor availability, ask for explicit patient confirmation, and safely create the appointment.

A key requirement is that an ambiguous response must not be treated as authorization to book an appointment.

## 2. Approach

I built a small Python-based agent using OpenAI tool calling, SQLite, FastAPI, Pydantic, and pytest.

The main components are:

- **OpenAI API** — natural-language understanding and tool calling
- **SQLite** — doctor and appointment data
- **Python tools** — availability checking and appointment booking
- **Deterministic validation** — confirmation validation before booking
- **Pytest** — functional and regression testing
- **Evaluation harness** — behavioral scenario testing and failure analysis

The agent provides two primary tools:

1. `check_availability`
2. `book_appointment`

Conversation history is maintained across turns so information collected earlier can be reused.

For the booking operation, I deliberately do not rely entirely on the LLM. The application independently validates that the patient's latest message represents explicit confirmation before creating the appointment.

## 3. Evaluation

I created three behavioral scenarios:

1. Successful booking after explicit confirmation
2. Ambiguous confirmation that must not result in booking
3. Unknown doctor that must not result in booking

The evaluator checks the actual SQLite database state rather than relying only on the assistant's response.

The initial evaluation produced:

```text
2/3 passed
66.7%

The failing scenario contained the patient response:

"Yes, please book it."

The original confirmation validator used exact string matching and therefore did not recognize the punctuation variant as an explicit confirmation.

4. Improvement

I converted the observed failure into a concrete implementation improvement.

The confirmation validation was changed to:

normalize punctuation
normalize whitespace
recognize natural confirmation variants

For example:

"Yes, please book it."

is normalized before being checked against the supported confirmation phrases.

The same evaluation scenarios were then run again.

The result improved to:

3/3 passed
100%

The existing automated tests were also executed after the change:

11/11 passed

Therefore, the improvement increased the behavioral evaluation score without causing a regression in the existing test suite.

The improvement loop is:

Evaluate
   ↓
Detect failure
   ↓
Identify root cause
   ↓
Implement targeted improvement
   ↓
Re-run the same scenarios
   ↓
Run regression tests
5. Design Trade-offs

I intentionally kept the architecture small and focused on agent reliability and evaluation.

I did not use a vector database, RAG, LangChain/LangGraph, microservices, or reinforcement learning because these components were not necessary for the scheduling problem.

For a state-changing operation such as appointment booking, deterministic validation provides a simpler and more predictable safety boundary than relying entirely on model behavior.

I also kept the evaluation independent from the agent implementation so that the evaluator can verify the actual database state.

AI Assistance and Engineering Judgment

AI tools were used during development for implementation ideas, debugging, code review, and documentation assistance.

I did not assume that generated code was correct. I validated the implementation using local tests and behavioral evaluation.

One important engineering decision was to separate model reasoning from critical business logic.

The LLM is responsible for understanding the conversation and using the available tools, while the application remains responsible for validating confirmation and performing the actual database mutation.

When the evaluation exposed the confirmation failure, I used the observed behavior to make a targeted change rather than simply changing the expected evaluation result.