from .base import BaseStrategy, SystemResponseType
from touche_rad.core.context import DebateContext


class AlwaysDefendStrategy(BaseStrategy):
    """
    Always defends against the user's utterance by clarifying or supporting
    the system's previous stance. This strategy never attacks the user's
    position and focuses on maintaining the system's argumentative position.
    """

    name = "always_defend"

    def get_response_type(self, context: DebateContext) -> SystemResponseType:
        return SystemResponseType.DEFEND

    def generate_response(self, context: DebateContext) -> str:
        user_utterance = context.last_user_message
        # Simplified defense. In a real strategy, you would use relevant_arguments
        return f"I understand your point in '{user_utterance}', but I'd like to clarify my position."
