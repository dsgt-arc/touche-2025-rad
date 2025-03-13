import json
from transitions import Machine
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class DebateStateMachine(Machine):
    """The Debate FSM"""

    def __init__(self, model, config_file="transitions.json", **kwargs):
        """Initialize the debate state machine"""
        try:
            config = self.load_fsm_config(config_file)
            states = config["states"]
            transitions = config["transitions"]
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Error loading FSM configuration: {e}")
            raise e

        super().__init__(
            model=model,
            states=states,
            transitions=transitions,
            initial="awaiting_user_claim",
            auto_transitions=False,
            **kwargs,
        )

        logger.info(
            f"Debate state machine initialized with {len(states)} states and {len(transitions)} transitions"
        )

    def load_fsm_config(self, config_file: str) -> Dict[str, Any]:
        """Load and validate FSM configuration from a JSON file."""
        with open(config_file, "r") as f:
            config = json.load(f)

        if "states" not in config:
            raise ValueError("FSM configuration missing 'states' field")
        if "transitions" not in config:
            raise ValueError("FSM configuration missing 'transitions' field")

        return config
