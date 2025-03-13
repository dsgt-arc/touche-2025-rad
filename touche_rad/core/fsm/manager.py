from typing import Any, Dict, List
from .fsm import DebateStateMachine
import logging

logger = logging.getLogger(__name__)


class DebateContext:
    """The debate context"""

    def __init__(
        self,
        user_claim: str,
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
        self.state = None  # attached when passed into the DebateStateMachine

    def _generate_debate_id(self):
        """Generate a unique ID for this debate."""
        import uuid

        return str(uuid.uuid4())


class DebateManager:
    def __init__(
        self,
        strategy_engine=None,
        config_file="transitions.json",
    ):
        self.strategy_engine = strategy_engine
        self.context = DebateContext()
        self.machine = DebateStateMachine(self.context, config_file=config_file)

    # ----------------#
    #     Getters     #
    # ----------------#

    def get_debate_state(self) -> Dict[str, Any]:
        """Get the current state of the debate."""
        return {"state": self.state, "context": self.context}

    # ------------------#
    #    Entrypoint     #
    # ------------------#
    def handle_user_message(self, message: str) -> str:
        """Main entry point for handling a user message from streamlit app"""
        pass

    # ------------------#
    #    Conditions     #
    # ------------------#
    def debate_should_continue(self):
        """Check if the debate should continue."""
        pass

    def debate_should_conclude(self):
        """Check if the debate should conclude."""
        pass

    # ----------------#
    #    Handlers     #
    # ----------------#
    def on_enter_awaiting_user_claim(self):
        """Handler for entering awaiting_user_claim state"""
        pass

    def on_enter_processing_user_claim(self):
        """Handler for entering processing_user_claim state"""
        pass

    def on_enter_retrieving_response_data(self):
        """Handler for entering retrieving_response_data state"""
        pass

    def on_enter_generating_system_response(self):
        """Handler for entering generating_system_response state"""
        pass

    def on_enter_validating_debate(self):
        """Handler for entering validating_debate state"""
        pass

    def on_enter_suggesting_conclusion(self):
        """Handler for entering suggesting_conclusion state"""
        pass

    def on_enter_sending_system_response(self):
        """Handler for entering sending_system_response state"""
        pass

    def on_enter_awaiting_user_response(self):
        """Handler for entering awaiting_user_response state"""
        pass
