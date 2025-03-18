import pytest
from touche_rad.core.manager import DebateManager


def test_debate_manager_initial_claim():
    manager = DebateManager()
    _ = manager.handle_user_message("My claim is that the sky is blue.")
    assert manager.context.user_claim == "My claim is that the sky is blue."


def test_debate_manager_new_topic():
    manager = DebateManager()
    _ = manager.handle_user_message("message")
    response = manager.handle_user_message("new topic")
    assert "What's your claim?" in response
    assert manager.context.user_claim is None  # Should be reset


def test_debate_manager_conclusion_agreed():
    manager = DebateManager()
    manager.context.current_turn = manager.context.max_turns
    response = manager.handle_user_message("message")
    # manager.handle_user_message("message")
    assert manager.context.should_conclude() is True
    assert response == "I think we've reached a good point to conclude. Do you agree?"

    response = manager.handle_user_message("yes")
    assert response == "Great! It was a pleasure debating with you."
    assert manager.context.current_turn == 0


def test_debate_manager_conclusion_rejected():
    manager = DebateManager()
    manager.context.current_turn = manager.context.max_turns
    manager.handle_user_message("message")  # user turn
    manager.handle_user_message("message")  # trigger conclusion
    _ = manager.handle_user_message("no")  # Reject
    assert manager.context.conclusion_requested is True  # Remains requested


def test_debate_manager_invalid_state():
    manager = DebateManager()
    manager.context.state = "invalid_state"
    with pytest.raises(ValueError):
        manager.handle_user_message("This should raise an error.")
