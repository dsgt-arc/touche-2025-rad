from touche_rad.core.context import DebateContext
from touche_rad.core.machine import DebateMachine


def test_debate_machine_initialization():
    context = DebateContext()
    _ = DebateMachine(model=context)
    assert context.state == "user_turn"  # Initial state
    assert context.conclusion_requested is False


def test_debate_machine_transitions():
    context = DebateContext()
    _ = DebateMachine(model=context)

    # User input -> System turn
    context.user_input("User utterance")
    assert context.state == "system_turn"
    assert context.user_utterances == ["User utterance"]
    assert context.current_turn == 1
    assert context.last_user_message == "User utterance"

    # System response -> User turn
    context.system_response("System utterance")
    assert context.state == "user_turn"
    assert context.system_utterances == ["System utterance"]

    # Request conclusion
    context.current_turn = context.max_turns  # Simulate reaching max turns
    context.user_input("message")
    context.request_conclusion()  # now we request conclusion
    assert context.state == "conclusion"
    assert context.conclusion_requested is True

    # User approves conclusion
    context.user_approves_to_conclude()
    assert context.state == "user_turn"
    assert context.user_claim is None  # Debate reset
    assert context.conclusion_requested is False

    # Start a new debate
    context = DebateContext()
    _ = DebateMachine(model=context)
    context.user_input("new topic")
    context.start_new_debate()
    assert context.state == "user_turn"
    assert context.user_claim is None

    # Go back to conclusion
    context.current_turn = context.max_turns
    context.user_input("message")
    context.request_conclusion()  # Conclusion
    assert context.state == "conclusion"

    # User rejects conclusion
    context.user_rejects_to_conclude()
    assert context.state == "system_turn"
    assert context.conclusion_requested is True  # Stays True
