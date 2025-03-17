from transitions import Machine
import logging

logger = logging.getLogger(__name__)


class DebateMachine(Machine):
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

    transitions = [
        {
            "trigger": "receive_claim",
            "source": "awaiting_user_claim",
            "dest": "processing_user_claim",
        },
        {
            "trigger": "claim_processed",
            "source": "processing_user_claim",
            "dest": "retrieving_response_data",
        },
        {
            "trigger": "data_retrieved",
            "source": "retrieving_response_data",
            "dest": "generating_system_response",
        },
        {
            "trigger": "response_generated",
            "source": "generating_system_response",
            "dest": "validating_debate",
        },
        {
            "trigger": "should_continue",
            "source": "validating_debate",
            "dest": "sending_system_response",
            "conditions": ["debate_should_continue"],
        },
        {
            "trigger": "should_conclude",
            "source": "validating_debate",
            "dest": "suggesting_conclusion",
            "conditions": ["debate_should_conclude"],
        },
        {
            "trigger": "user_approves_to_conclude",
            "source": "suggesting_conclusion",
            "dest": "awaiting_user_claim",
        },
        {
            "trigger": "user_reject_to_conclude",
            "source": "suggesting_conclusion",
            "dest": "sending_system_response",
        },
        {
            "trigger": "system_response_sent",
            "source": "sending_system_response",
            "dest": "awaiting_user_response",
        },
        {
            "trigger": "receive_response",
            "source": "awaiting_user_response",
            "dest": "processing_user_claim",
        },
        {
            "trigger": "start_new_debate",
            "source": "awaiting_user_response",
            "dest": "awaiting_user_claim",
            "conditions": ["user_requests_new_topic"],
        },
    ]

    initial = "awaiting_user_claim"

    def __init__(self, **kwargs):
        """Initialize the debate state machine"""
        super().__init__(
            states=self.states,
            transitions=self.transitions,
            initial=self.initial,
            auto_transitions=False,
            **kwargs,
        )
