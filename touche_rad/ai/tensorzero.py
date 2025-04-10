import os
import json
from typing import Generator
from .base import ChatResourceEnum, EvaluationClient
from tensorzero import InferenceChunk, TensorZeroGateway, InferenceResponse


class TensorZeroChatResource(ChatResourceEnum):
    """Abstract base class for all TensorZero resources (models and functions)."""


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
        return cls.EVALUATE_UTTERANCE


class TensorZeroClient(EvaluationClient):
    """
    TensorZeroClient - a provider agnostic client to interface with the tensorzero gateway inference engine
    """

    def __init__(
        self,
    ):
        self._client = TensorZeroGateway(os.environ.get("TENSORZERO_GATEWAY_URL"))

    def _inference(
        self,
        fn: str,
        role: str,
        utterance: str,
        prev: str,
        user_claim: str,
    ) -> InferenceResponse | Generator[InferenceChunk, None, None]:
        return self._client.inference(
            function_name=fn,
            input={
                "messages": [
                    {
                        "role": role,
                        "content": [
                            {
                                "type": "text",
                                "arguments": {
                                    "argument": utterance,
                                    "previous_message": prev,
                                    "claim": user_claim,
                                },
                            }
                        ],
                    }
                ]
            },
        )

    def evaluate(self, ctx, role, utterance) -> dict[str, int]:
        if role == "user":
            previous_message = ctx.system_utterances[-1]
        else:
            previous_message = ctx.user_utterances[-1]

        try:
            res = (
                self._inference(
                    TensorZeroChatResourceFunction.EVALUATE_UTTERANCE,
                    role=role,
                    utterance=utterance,
                    prev=previous_message,
                    user_claim=ctx.user_claim,
                )
                .content[0]
                .text
            )

            try:
                data = json.loads(res)
                evaluation = [
                    data.get("quantity_score"),
                    data.get("quality_score"),
                    data.get("relation_score"),
                    data.get("manner_score"),
                ]

                return evaluation
            except Exception:
                pass  # for now

        except Exception as e:
            print(f"An error occurred during evaluation: {e}")
            return f"An error occurred during evaluation: {e}"
