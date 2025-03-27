from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List


class ChatResourceEnum(str, Enum):
    """
    Base API chat model enum for listing available models and providing a
    default model
    """

    @classmethod
    @abstractmethod
    def chat_models(cls) -> List["ChatResourceEnum"]:
        """
        Return the list of models that are supported for chat from specified client
        """
        pass

    @classmethod
    @abstractmethod
    def default_model(cls) -> "ChatResourceEnum":
        """
        Return the defined default model
        """
        pass


@dataclass
class Message:
    """
    Chat Message dataclass
    """

    role: str
    content: str


class ChatClient(ABC):
    """
    Base class to make interchangeable chat completion
    providers, similarly to how OpenAI provides an SDK of its own
    """

    @abstractmethod
    def chat(self, messages: List[Message]) -> str:
        """
        Send chat messages and return the response
        """
        pass
