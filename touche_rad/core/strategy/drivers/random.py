import random
from .base import BaseStrategy, SystemResponseType
from touche_rad.core.context import DebateContext


class RandomStrategy(BaseStrategy):
    """Chooses randomly between attack and defend, and generates canned responses."""

    name = "random"

    def __init__(self, attack_prob: float = 0.5):
        self.attack_prob = attack_prob
        self.attack_responses = [
            "That's an interesting point, but I disagree.",
            "I see what you mean, but have you considered the opposite?",
            "I'm not sure I agree with that.",
        ]
        self.defend_responses = [
            "You make a good point, and I'll clarify my previous statement.",
            "I understand your concern, but here's why I still believe...",
            "Perhaps I didn't explain it well.  Let me rephrase...",
        ]

    def get_response_type(self, context: DebateContext) -> SystemResponseType:
        if random.random() < self.attack_prob:
            return SystemResponseType.ATTACK
        else:
            return SystemResponseType.DEFEND

    def generate_response(self, context: DebateContext) -> str:
        if self.get_response_type(context) == SystemResponseType.ATTACK:
            return random.choice(self.attack_responses)
        else:
            return random.choice(self.defend_responses)
