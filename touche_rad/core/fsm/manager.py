from .context import DebateContext
from .machine import DebateMachine


class DebateManager(object):
    def __init__(self, strategy_engine=None):
        self.strategy_engine = strategy_engine
        self.context = DebateContext()
        self.machine = DebateMachine(model=self.context)

    def handle_user_message(self, message: str) -> str:
        """Main entry point for handling a user message."""

        if self.context.state == "user_turn":
            if self.context.user_requests_new_topic():
                self.context.start_new_debate()
                return "Okay, let's start a new debate.  What's your claim?"

            # Set the initial claim
            if not self.context.user_claim:
                self.context.user_claim = message

            self.context.user_input(message)

            # Simulate system processing
            system_response = self.generate_system_response(message)
            if self.context.should_conclude():
                self.context.request_conclusion()
                return "I think we've reached a good point to conclude. Do you agree?"

            # Trigger transition with the response
            self.context.system_response(system_response)
            return system_response

        elif self.context.state == "conclusion":
            if message.lower() in ("yes", "y", "ok", "sure"):
                self.context.user_approves_to_conclude()
                return "Great! It was a pleasure debating with you."
            else:
                self.context.user_rejects_to_conclude()
                system_response = self.generate_system_response(message)
                self.context.system_response(system_response)
                return system_response
        else:
            # Shouldn't happen, but good for debugging
            return "I'm not sure what to do right now."

    def generate_system_response(self, user_message):
        # should be replaced with strategy_engine, retrieval, and generation
        if self.context.current_turn == 1:
            return (
                "I disagree with your claim that "
                + self.context.user_claim
                + ".  Here's a counterargument..."
            )
        else:
            return (
                "In response to your point about '"
                + user_message
                + "', I'd like to say..."
            )
