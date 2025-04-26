import os
from typing import List

import requests
from .base import ChatResourceEnum, ChatClient, Message


class TextSynthEngine(ChatResourceEnum):
    """
    Available chat engines provided by the TextSynth API
    https://textsynth.com/documentation.html#engines
    """

    MISTRAL_7B = "mistral_7B"
    LLAMA3_8B = "llama3_8B"
    LLAMA3_1_8B_INSTRUCT = "llama3.1_8B_instruct"
    MIXTRAL_47B_INSTRUCT = "mixtral_47B_instruct"
    LLAMA3_3_70B_INSTRUCT = "llama3.3_70B_instruct"
    GPTJ_6B = "gptj_6B"

    @classmethod
    def default_model(cls) -> "TextSynthEngine":
        return cls.MISTRAL_7B

    @classmethod
    def chat_models(cls) -> List["TextSynthEngine"]:
        return [
            cls.MISTRAL_7B,
            cls.LLAMA3_8B,
            cls.LLAMA3_1_8B_INSTRUCT,
            cls.MIXTRAL_47B_INSTRUCT,
            cls.LLAMA3_3_70B_INSTRUCT,
            cls.GPTJ_6B,
        ]


class TextSynthClient(ChatClient):
    """
    TextSynth ChatClient
    """

    def __init__(
        self,
        api_key: str | None = os.environ.get("TEXTSYNTH_API_KEY"),
        engine_id: TextSynthEngine = TextSynthEngine.default_model(),
        system_prompt: str | None = None,
    ):
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("TEXTSYNTH_API_KEY environment variable not set")

        if engine_id not in TextSynthEngine.chat_models():
            raise ValueError(
                f"Invalid engine_id for chat. Must be one of: {', '.join(e.value for e in TextSynthEngine.chat_models())}"
            )

        self.engine_id = engine_id
        self.url = f"https://api.textsynth.com/v1/engines/{engine_id.value}/chat"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.system_prompt = system_prompt

    def chat(self, messages: List[Message]) -> str:
        request_body: dict[str, str | list[str]] = {
            "messages": [msg.content for msg in messages]
        }
        if self.system_prompt is not None:
            request_body["system"] = self.system_prompt

        response = requests.post(self.url, headers=self.headers, json=request_body)
        response.raise_for_status()
        return response.json()["text"].strip()
