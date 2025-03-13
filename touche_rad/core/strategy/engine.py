import random
from touche_rad.core.model.response import SystemResponseType


class StrategyEngine:
    def __init__(self):
        # TODO: actually implement a strategy instead of flipping a coin
        self.defend_probability = 0.5

    def get_strategy(
        self,
        user_utterance,
        relevant_arguments,
        debate_history,
        system_history,
        current_turn,
    ):
        if random.random() < self.defend_probability:
            return SystemResponseType.DEFEND
        else:
            return SystemResponseType.ATTACK

    def apply_strategy(
        self, strategy, user_utterance, relevant_arguments, system_history
    ):
        """
        Strategy application to decide whether to defend or attack. Note that the system MUST attack upon the initial user message (the claim)
        """
        if strategy == SystemResponseType.DEFEND:
            if system_history:
                # TODO: we need to handle the system deciding which prev system utterance the user is referring to
                response_to_defend = system_history[-1]
                return self._generate_defense(response_to_defend, user_utterance)
            else:
                return self._generate_attack(user_utterance, relevant_arguments)
        else:
            return self._generate_attack(user_utterance, relevant_arguments)

    def _generate_defense(self, response_to_defend, user_utterance):
        pass

    def _generate_attack(self, user_utterance, relevant_arguments):
        pass
