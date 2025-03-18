from .context import DebateContext
from .machine import DebateMachine
from .strategy import create_strategy


class DebateManager(object):
    def __init__(self, strategy_name: str = "random"):
        self.strategy = create_strategy(strategy_name)
        self.context = DebateContext()
        self.machine = DebateMachine(model=self.context)

    def handle_user_message(self, message: str) -> str:
        """Main entry point for handling a user message."""

        if self.context.is_user_turn():
            if self.context.user_requests_new_topic():
                self.context.start_new_debate()
                return "Okay, let's start a new debate.  What's your claim?"

            # Set the initial claim
            if not self.context.user_claim:
                self.context.user_claim = message

            self.context.user_input(message)
            system_response = self.strategy.generate_response(self.context)
            if self.context.should_conclude():
                self.context.request_conclusion()
                return "I think we've reached a good point to conclude. Do you agree?"

            # Trigger transition with the response
            self.context.system_response(system_response)
            return system_response

        elif self.context.is_conclusion():
            if message.lower() in ("yes", "y", "ok", "sure"):
                self.context.user_approves_to_conclude()
                return "Great! It was a pleasure debating with you."
            else:
                self.context.user_rejects_to_conclude()
                system_response = self.strategy.generate_response(self.context)
                self.context.system_response(system_response)
                return system_response
        else:
            return "I'm not sure what to do right now."
