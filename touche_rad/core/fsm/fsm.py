from transitions import Machine
import logging

logger = logging.getLogger(__name__)


class DebateStateMachine(Machine):
    """The Debate FSM"""

    states = [
        "awaiting_user_claim",
        "processing_user_claim",
        "retrieving_response_data",
        "generating_system_response",
        "validating_debate",
        "suggesting_conclusion",
        "sending_system_response",
        "awaiting_user_response",
    ]

    def __init__(self, model, **kwargs):
        """Initialize the debate state machine"""
        super().__init__(
            model=model,
            states=DebateStateMachine.states,
            initial="awaiting_user_claim",
            auto_transitions=False,
            **kwargs,
        )

        self.add_transition(
            "receive_claim", "awaiting_user_claim", "processing_user_claim"
        )
        self.add_transition(
            "claim_processed", "processing_user_claim", "retrieving_response_data"
        )
        self.add_transition(
            "data_retrieved", "retrieving_response_data", "generating_system_response"
        )
        self.add_transition(
            "response_generated", "generating_system_response", "validating_debate"
        )

        self.add_transition(
            "should_continue",
            "validating_debate",
            "sending_system_response",
            conditions=["debate_should_continue"],
        )

        self.add_transition(
            "should_conclude",
            "validating_debate",
            "suggesting_conclusion",
            conditions=["debate_should_conclude"],
        )

        self.add_transition(
            "user_approves_to_conclude", "suggesting_conclusion", "awaiting_user_claim"
        )
        self.add_transition(
            "user_reject_to_conclude",
            "suggesting_conclusion",
            "sending_system_response",
        )
        self.add_transition(
            "system_response_sent", "sending_system_response", "awaiting_user_response"
        )
        self.add_transition(
            "receive_response", "awaiting_user_response", "processing_user_claim"
        )

        self.add_transition(
            "start_new_debate",
            "awaiting_user_response",
            "awaiting_user_claim",
            conditions=["user_requests_new_topic"],
        )
