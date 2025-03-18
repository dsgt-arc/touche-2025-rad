class DebateContext(object):
    """The debate context"""

    def __init__(
        self,
        user_utterances: list[str] = None,
        system_utterances: list[str] = None,
        current_turn: int = 0,
        max_turns: int = 5,
        conclusion_requested: bool = False,
        debate_id: str = None,
    ):
        self.debate_id = debate_id or self._generate_id()
        self.user_utterances = user_utterances or []
        self.system_utterances = system_utterances or []
        self.current_turn = current_turn
        self.max_turns = max_turns
        self.conclusion_requested = conclusion_requested

    @property
    def user_claim(self) -> str | None:
        if not self.user_utterances:
            return None
        return self.user_utterances[0]

    @property
    def last_user_message(self) -> str | None:
        if not self.user_utterances:
            return None
        return self.user_utterances[-1]

    def reset_debate(self):
        """Reset the debate context to its initial state."""
        self.user_utterances = []
        self.system_utterances = []
        self.current_turn = 0
        self.conclusion_requested = False
        self.debate_id = self._generate_id()

    def _generate_id(self):
        """Generate a unique ID for this debate."""
        import uuid

        return str(uuid.uuid4())

    def should_conclude(self):
        """Check if the debate should conclude."""
        return self.conclusion_requested or self.current_turn >= self.max_turns

    def user_requests_new_topic(self):
        """Check if user has requested a new topic."""
        if not self.last_user_message:
            return False
        return self.last_user_message.lower() == "new topic"

    def add_user_utterance(self, utterance: str):
        self.user_utterances.append(utterance)
        self.current_turn += 1
        if self.current_turn >= self.max_turns:
            self.conclusion_requested = True

    def add_system_utterance(self, utterance: str):
        self.system_utterances.append(utterance)
