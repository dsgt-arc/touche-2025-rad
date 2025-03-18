import pytest
from touche_rad.core.context import DebateContext


def test_debate_context_reset_debate():
    context = DebateContext(
        user_utterances=["User 1"],
        system_utterances=["Sys 1"],
        current_turn=5,
        conclusion_requested=True,
    )
    old_debate_id = context.debate_id
    context.reset_debate()
    assert context.user_claim is None
    assert context.user_utterances == []
    assert context.system_utterances == []
    assert context.conclusion_requested is False
    assert context.last_user_message is None
    assert context.debate_id != old_debate_id  # A new UUID should be generated.


def test_debate_context_should_conclude():
    context = DebateContext(max_turns=5)
    assert context.should_conclude() is False
    context.current_turn = 5
    assert context.should_conclude() is True
    context.conclusion_requested = True
    assert context.should_conclude() is True
    context.current_turn = 4
    context.conclusion_requested = False
    assert context.should_conclude() is False
    context.current_turn = 6
    assert context.should_conclude() is True


@pytest.mark.parametrize(
    "user_input, expected",
    [
        ("New Topic", True),
        ("new topic", True),
        ("New topic", True),
        ("Another message", False),
        ("new topic please", False),
        ("", False),
        (None, False),
    ],
)
def test_debate_context_user_requests_new_topic(user_input, expected):
    context = DebateContext()
    assert context.user_requests_new_topic() is False
    context.add_user_utterance(user_input)
    assert context.user_requests_new_topic() is expected


def test_add_utterance():
    context = DebateContext()

    context.add_user_utterance("Hello")
    assert context.user_utterances == ["Hello"]
    assert context.current_turn == 1
    assert context.last_user_message == "Hello"

    context.add_system_utterance("Hi")
    assert context.system_utterances == ["Hi"]
