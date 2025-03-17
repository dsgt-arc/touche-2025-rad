from .machine import DebateMachine
from .context import DebateContext


class DebateManager(object):
    def __init__(
        self,
        strategy_engine=None,
    ):
        self.strategy_engine = strategy_engine
        self.context = DebateContext()
        self.machine = DebateMachine(model=self.context)

    def handle_user_message(self, message: str) -> str:
        """Main entry point for handling a user message from streamlit app"""
        if self.context.state == "awaiting_user_claim":
            self.context.receive_claim()
        elif self.context.state == "processing_user_claim":
            self.context.claim_processed()

        return self.context.state
