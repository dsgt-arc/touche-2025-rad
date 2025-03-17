class DebateContext(object):
    """The debate context"""

    def __init__(
        self,
        user_claim: str = None,
        user_utterances: list[str] = None,
        system_utterances: list[str] = None,
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
        self.last_user_message: str | None = None

    def reset_debate(self):
        """Reset the debate context to its initial state."""
        self.user_claim = None
        self.user_utterances = []
        self.system_utterances = []
        self.current_turn = 0
        self.conclusion_requested = False
        self.last_user_message = None
        self.debate_id = self._generate_id()

    def _generate_id(self):
        """Generate a unique ID for this debate."""
        import uuid

        return str(uuid.uuid4())

    def should_continue(self):
        """Check if the debate should continue."""
        return self.current_turn < self.max_turns and not self.conclusion_requested

    def should_conclude(self):
        """Check if the debate should conclude."""
        return self.current_turn >= self.max_turns or self.conclusion_requested

    def user_requests_new_topic(self):
        """Check if user has requested a new topic.  Simplified for demonstration."""
        return self.last_user_message and self.last_user_message.lower() == "new topic"

    def add_user_utterance(self, utterance: str):
        self.user_utterances.append(utterance)
        self.current_turn += 1
        self.last_user_message = utterance

    def add_system_utterance(self, utterance: str):
        self.system_utterances.append(utterance)
