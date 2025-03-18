from .base import BaseStrategy, SystemResponseType
from touche_rad.core.fsm import DebateContext


class AlwaysAttackStrategy(BaseStrategy):
    """Always attacks the user's utterance."""

    name = "always_attack"

    def get_response_type(self, context: DebateContext) -> SystemResponseType:
        return SystemResponseType.ATTACK

    def generate_response(self, context: DebateContext) -> str:
        user_utterance = context.last_user_message
        return f"I disagree with your statement: '{user_utterance}'."
