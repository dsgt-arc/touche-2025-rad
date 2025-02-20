import os
from typing import List
from .base import ChatModelEnum, ChatClient, Message
from tensorzero import TensorZeroGateway, InferenceResponse


class TensorZeroModel(ChatModelEnum):
    """
    Available models provided via TensorZero and configured functions
    """

    # openai models
    GPT4_O = "openai::gpt-4o"
    GPT4_O_LATEST = "openai::chatgpt-4o-latest"
    GPT4_O_MINI = "openai::gpt-4o-mini"

    # anthropic models (just adding as an example)
    SONNET3_5 = "anthropic::claude-3-5-sonnet-latest"

    # tensorzero functions
    CHAT_COMPLETION = "tensorzero::function_name::chat_completion"
    SUMMARIZE_DATA = "tensorzero::function_name::summarize_data"

    @classmethod
    def default_model(cls) -> "TensorZeroModel":
        return cls.GPT4_O_MINI

    @classmethod
    def chat_models(cls) -> List["TensorZeroModel"]:
        return [cls.GPT4_O, cls.GPT4_O_LATEST, cls.GPT4_O_MINI, cls.GENERATE_HAIKU]


class TensorZeroClient(ChatClient):
    """
    TensorZeroClient - a provider agnostic client to interface with the tensorzero gateway inference engine
    """

    def __init__(
        self,
        model: TensorZeroModel = TensorZeroModel.default_model(),
    ):
        self._client = TensorZeroGateway(os.environ.get("TENSORZERO_GATEWAY_URL"))
        self.model = model

    def chat(self, messages: List[Message]) -> str:
        with self._client as client:
            response: InferenceResponse = client.inference(
                model_name=self.model,
                input={
                    "messages": [
                        {"role": msg.role, "content": msg.content} for msg in messages
                    ]
                },
            )
            return response.content[0].text
