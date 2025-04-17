import os
import json
from typing import Generator, List, Union

from touche_rad.core.context import DebateContext
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
        payload_role = "assistant" if role == "system" else role
        return self._client.inference(
            function_name=fn,
            input={
                "messages": [
                    {
                        "role": payload_role,
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

    def evaluate(
        self, ctx: DebateContext, role: str, utterance: str
    ) -> Union[List[Union[int, None]], str]:
        """Evaluates an utterance, handling potential errors and None claim."""
        if role == "user":
            previous_message = (
                "" if len(ctx.system_utterances) == 0 else ctx.system_utterances[-1]
            )
            current_claim = ctx.user_claim
            if current_claim is None:
                current_claim = utterance
        else:
            previous_message = (
                "" if len(ctx.user_utterances) == 0 else ctx.user_utterances[-1]
            )
            current_claim = ctx.user_claim
            if current_claim is None:
                current_claim = ""

        try:
            res_obj = self._inference(
                TensorZeroChatResourceFunction.EVALUATE_UTTERANCE,
                role="user",
                utterance=utterance,
                prev=previous_message,
                user_claim=current_claim,
            )

            if isinstance(res_obj, InferenceResponse):
                res = res_obj.content[0].text
            else:
                raise TypeError(
                    f"Unexpected response type from inference: {type(res_obj)}"
                )

            try:
                data = json.loads(res)

                if not all(
                    k in data
                    for k in [
                        "quantity_score",
                        "quality_score",
                        "relation_score",
                        "manner_score",
                    ]
                ):
                    raise ValueError(
                        f"Evaluation response missing required score fields. Received: {res}"
                    )

                evaluation = [
                    data.get("quantity_score"),
                    data.get("quality_score"),
                    data.get("relation_score"),
                    data.get("manner_score"),
                ]

                evaluation = [int(s) if s is not None else None for s in evaluation]

                return evaluation

            except (json.JSONDecodeError, ValueError, KeyError, TypeError) as json_err:
                error_msg = f"Error processing evaluation response: {json_err}. Raw response: '{res}'"
                print(error_msg)
                return f"An error occurred during evaluation: {error_msg}"

        except Exception as e:
            error_msg = f"An error occurred calling evaluation service: {e}"
            return f"An error occurred during evaluation: {error_msg}"
