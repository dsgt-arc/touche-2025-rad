import uuid

from typing import List, Optional
from uuid_utils import compat


class DebateContext(object):
    """The debate context"""

    def __init__(
        self,
        client,
        user_utterances: list[str] = None,
        system_utterances: list[str] = None,
        current_turn: int = 0,
        max_turns: int = 3,
        conclusion_requested: bool = False,
        debate_id: uuid.UUID = None,
    ):
        self.debate_id = debate_id or self._generate_id()
        self.client = client
        self.user_utterances = user_utterances or []
        self.system_utterances = system_utterances or []
        self.user_ratings = []
        self.system_ratings = []
        self.current_turn = current_turn
        self.max_turns = max_turns
        self.conclusion_requested = conclusion_requested

    @property
    def user_claim(self) -> Optional[str]:
        if not self.user_utterances:
            return None
        return self.user_utterances[0]

    @property
    def last_user_message(self) -> Optional[str]:
        if not self.user_utterances:
            return None
        return self.user_utterances[-1]

    def get_conversation(self) -> List[str]:
        conversation = []
        user_len = len(self.user_utterances)
        system_len = len(self.system_utterances)
        max_len = max(user_len, system_len)

        for i in range(max_len):
            if i < user_len:
                conversation.append(self.user_utterances[i])
            # Ensure system utterance exists and is not None/empty before appending
            if i < system_len and self.system_utterances[i]:
                conversation.append(self.system_utterances[i])
        return conversation

    def reset_debate(self):
        """Reset the debate context to its initial state."""
        self.user_utterances = []
        self.system_utterances = []
        self.user_ratings = []
        self.system_ratings = []
        self.current_turn = 0
        self.conclusion_requested = False
        self.debate_id = self._generate_id()

    def _generate_id(self):
        """Generate a unique ID for this debate."""
        return compat.uuid7()

    def should_conclude(self):
        """Check if the debate should conclude."""
        return self.conclusion_requested or self.current_turn >= self.max_turns

    def user_requests_new_topic(self):
        """Check if user has requested a new topic."""
        if not self.last_user_message:
            return False
        return self.last_user_message.lower() == "new topic"

    def add_user_utterance(self, utterance: str):
        if self.user_claim is not None:
            self._evaluate_user_utterance(utterance=utterance)

        self.user_utterances.append(utterance)
        self.current_turn = self.current_turn + 1
        if self.current_turn >= self.max_turns:
            self.conclusion_requested = True

    def add_system_utterance(self, utterance: str):
        if len(self.user_utterances) > 0:
            self._evaluate_system_utterance(utterance=utterance)
            self.system_utterances.append(utterance)

    def _evaluate_user_utterance(self, utterance: str):
        score = self.client.evaluate(ctx=self, role="user", utterance=utterance)
        self.user_ratings.append(score)

    def _evaluate_system_utterance(self, utterance: str):
        score = self.client.evaluate(ctx=self, role="system", utterance=utterance)
        self.system_ratings.append(score)
