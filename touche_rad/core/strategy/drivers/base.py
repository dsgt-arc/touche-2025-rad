from abc import ABC, abstractmethod
from enum import Enum, auto
from touche_rad.core.fsm import DebateContext


class SystemResponseType(Enum):
    DEFEND = auto()
    ATTACK = auto()


class BaseStrategy(ABC):
    """
    Abstract base class for debate strategies.  Defines the interface
    that all concrete strategies must implement.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the strategy."""
        pass

    @abstractmethod
    def get_response_type(self, context: DebateContext) -> SystemResponseType:
        """
        Determines the *type* of response (attack or defend).  This is the
        high-level strategic decision.

        Args:
            user_utterance: The current user's utterance.
            context:  A dictionary containing information about the
                debate state (history, current turn, etc.).

        Returns:
            SystemResponseType:  ATTACK or DEFEND.
        """
        pass

    @abstractmethod
    def generate_response(self, context: DebateContext) -> str:
        """
        Generates the actual text of the response, based on the chosen
        response type and relevant arguments.

        Args:
            user_utterance: The current user's utterance.
            context: A dictionary containing information about the debate.
            relevant_arguments: A list of dictionaries, each representing a
                relevant argument (e.g., {'text': '...', 'stance': '...'}).

        Returns:
            str: The generated response text.
        """
        pass
