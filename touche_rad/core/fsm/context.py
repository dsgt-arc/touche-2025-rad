from typing import Any, List


class DebateContext(object):
    """The debate context"""

    def __init__(
        self,
        user_claim: str = None,
        user_utterances: List[Any] = None,
        system_utterances: List[Any] = None,
        current_turn: int = 0,
        max_turns: int = 20,
        conclusion_requested: bool = False,
        debate_id: str = None,
    ):
        # TODO: add methods to modify the contents of the context
        self.debate_id = debate_id or self._generate_id()
        self.user_claim = user_claim
        self.user_utterances = user_utterances or []
        self.system_utterances = system_utterances or []
        self.current_turn = current_turn
        self.max_turns = max_turns
        self.conclusion_requested = conclusion_requested

    def _generate_id(self):
        """Generate a unique ID for this debate."""
        import uuid

        return str(uuid.uuid4())

    # Define methods needed for FSM conditions
    def should_continue(self):
        """Check if the debate should continue."""
        return self.current_turn < self.max_turns and not self.conclusion_requested

    def should_conclude(self):
        """Check if the debate should conclude."""
        return self.current_turn >= self.max_turns or self.conclusion_requested

    def user_requests_new_topic(self):
        """Check if user has requested a new topic."""
        raise NotImplementedError("not implemented")
