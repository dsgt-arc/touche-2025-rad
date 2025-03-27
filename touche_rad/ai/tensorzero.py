import os
from typing import Any, Dict, List, Union
from .base import ChatClient, ChatResourceEnum, Message
from tensorzero import TensorZeroGateway, InferenceResponse


class TensorZeroChatResource(ChatResourceEnum):
    """Abstract base class for all TensorZero resources (models and functions)."""

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name


class TensorZeroChatResourceModel(TensorZeroChatResource):
    """
    Available chat models provided via TensorZero.
    """

    GPT4_O = "openai::gpt-4o"
    GPT4_O_LATEST = "openai::chatgpt-4o-latest"
    GPT4_O_MINI = "openai::gpt-4o-mini"

    @classmethod
    def default_model(cls) -> "TensorZeroChatResourceModel":
        return cls.GPT4_O_MINI


class TensorZeroChatResourceFunction(TensorZeroChatResource):
    """
    Available chat functions configured via TensorZero.
    """

    EVALUATE_UTTERANCE = "evaluate_utterance"

    @classmethod
    def default_model(cls) -> "TensorZeroChatResourceFunction":
        return cls.GPT4_O_MINI

    @classmethod
    def chat_models(cls) -> List["TensorZeroChatResourceFunction"]:
        return [cls.EVALUATE_UTTERANCE]


class TensorZeroClient(ChatClient):
    """
    TensorZeroClient - a provider agnostic client to interface with the tensorzero gateway inference engine
    """

    def __init__(
        self,
    ):
        self._client = TensorZeroGateway(os.environ.get("TENSORZERO_GATEWAY_URL"))

    def chat(
        self,
        messages: List[Message],
        resource: Union[
            TensorZeroChatResourceModel, TensorZeroChatResourceFunction
        ] = None,
    ):
        """
        Chats with the TensorZero gateway using the specified model or function.

        Args:
            messages: A list of messages to send to the model.
            resource: Either a TensorZeroChatResourceModel or a
                TensorZeroChatResourceFunction object.  If None, the default model is used.

        Returns:
            The response from the model.
        """

        with self._client as client:
            input_data: Dict[str, Any] = {
                "messages": [
                    {"role": msg.role, "content": msg.content} for msg in messages
                ]
            }

            if resource is None:
                resource = TensorZeroChatResourceModel.default_model()

            resource_name = resource.name
            is_function = isinstance(resource, TensorZeroChatResourceFunction)

            if is_function:
                response: InferenceResponse = client.call_function(
                    function_name=resource_name, input=input_data
                )
            else:
                response: InferenceResponse = client.inference(
                    model_name=resource_name, input=input_data
                )

            return response.content[0].text
