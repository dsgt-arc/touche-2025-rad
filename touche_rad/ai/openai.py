import os
from typing import List
from .base import ChatModelEnum, ChatClient, Message
from openai import OpenAI


class OpenAIModel(ChatModelEnum):
    """
    Available chat models provided by the OpenAI Chat API
    """

    GPT4_O = "gpt-4o"
    GPT4_O_LATEST = "chatgpt-4o-latest"
    GPT4_O_MINI = "gpt-4o-mini"

    # TODO: support reasoning models?
    # O1 = "o1"
    # O1_MINI = "o1-mini"
    # O3_MINI = "o3-mini"
    # O1_PREVIEW = "o1-preview"

    @classmethod
    def default_model(cls) -> "OpenAIModel":
        return cls.GPT4_O

    @classmethod
    def chat_models(cls) -> List["OpenAIModel"]:
        return [
            cls.GPT4_O,
            cls.GPT4_O_LATEST,
            cls.GPT4_O_MINI,
            # cls.O1,
            # cls.O1_MINI,
            # cls.O3_MINI,
            # cls.O1_PREVIEW,
        ]

    # @classmethod
    # def reasoning_models(cls) -> List["OpenAIModel"]:
    #     return [
    #         cls.O1,
    #         cls.O1_MINI,
    #         cls.O3_MINI,
    #         cls.O1_PREVIEW
    #     ]


class OpenAIClient(ChatClient):
    """
    OpenAIChatClient - can also support other providers that enable the leveraging
    of the OpenAI SDK with their API
    """

    def __init__(
        self,
        api_key: str | None = os.environ.get("OPENAI_API_KEY"),
        url: str | None = None,
        model: OpenAIModel = OpenAIModel.default_model(),
    ):
        self._client = (
            OpenAI(api_key=api_key, base_url=url) if url else OpenAI(api_key=api_key)
        )
        self.model = model

    @property
    def client(self):
        return self._client

    def chat(self, messages: List[Message]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": msg.role, "content": msg.content} for msg in messages],
        )
        return response.choices[0].message.content
