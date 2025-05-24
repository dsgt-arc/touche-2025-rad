from typing import List, Any
import os
from jinja2 import Environment, PackageLoader, select_autoescape
from openai import OpenAI
import yaml
from pathlib import Path
import json
import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from touche_rad.ai.elasticsearch_retriever import ElasticsearchRetriever
import cachetools

MAX_RETRIES = 5

load_dotenv()
env = Environment(loader=PackageLoader("app"), autoescape=select_autoescape())
logger = logging.getLogger(__name__)


class Message(BaseModel):
    role: str
    content: str


class Request(BaseModel):
    messages: List[Message]


class Topic(BaseModel):
    description: str


class Configuration(BaseModel):
    topic: Topic
    user: Any
    system: Any
    maxTurns: int


class Argument(BaseModel):
    id: str
    text: str


class RetrievalResponse(BaseModel):
    arguments: List[Argument]


class SystemResponse(BaseModel):
    utterance: str
    response: RetrievalResponse


class UserTurn(BaseModel):
    utterance: str
    systemResponse: SystemResponse


class Simulation(BaseModel):
    configuration: Configuration
    userTurns: List[UserTurn]
    milliseconds: float


class GenIREvalRequest(BaseModel):
    simulation: Simulation
    userTurnIndex: int | None = None


class AppEvalRequest(BaseModel):
    issue: str
    argument: str
    counter_argument: str

    # make this hashable
    def __hash__(self):
        return hash((self.issue, self.argument, self.counter_argument))


class EvalScore(BaseModel):
    score: float
    explanation: str


class EvalResponse(BaseModel):
    quantity: EvalScore
    quality: EvalScore
    relation: EvalScore
    manner: EvalScore


app = FastAPI()

retriever = ElasticsearchRetriever()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


def get_model(model):
    # a list of supported models
    supported_models = [
        "openai/gpt-4o",
        "openai/gpt-4.1",
        "anthropic/claude-sonnet-4",
        "anthropic/claude-opus-4",
        "google/gemini-2.5-pro-preview",
        "google/gemini-2.5-flash-preview-05-20",
    ]
    mapping = {name.split("/")[-1]: name for name in supported_models}
    # purposely crash if we're not in the list
    if model not in mapping:
        raise ValueError(f"Model {model} is not supported.")
    return mapping[model]


@app.post("/respond/{model_name}")
async def respond(request: Request, model_name: str):
    # get the message for user and assistant
    # we're given some odd number of messages that need to be placed into the context appropriately
    logging.info(request)
    # let's generate the prompt that we want to use
    evidence = retriever.retrieve(
        request.messages[0].content,
        mode="text",
        k=10,
    )
    # let's generate a yaml document that contains topic, tags, text, and references
    subset = [
        {k: v for k, v in item.items() if k in ["topic", "text"]} for item in evidence
    ]
    prompt = env.get_template("prompt.md.j2").render(
        evidence=yaml.dump(subset),
        context=request.messages[-1].content,
    )

    model_fqn = get_model(model_name)
    for attempt in range(MAX_RETRIES):
        try:
            completion = client.chat.completions.create(
                model=model_fqn,
                messages=request.messages
                + [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
            content = completion.choices[0].message.content
            if not content:
                raise ValueError("Empty response from model.")
            break
        except Exception as e:
            logger.error(
                f"Attempt {attempt + 1}/{MAX_RETRIES}: Error during response generation: {e}"
            )
            if attempt == MAX_RETRIES - 1:
                return {"error": f"Failed after {MAX_RETRIES} attempts: {str(e)}"}
    resp = {"content": content, "arguments": evidence}
    if os.environ.get("LOG_PATH"):
        log_path = Path(os.environ.get("LOG_PATH")) / "respond"
        log_path.mkdir(parents=True, exist_ok=True)
        with open(log_path / f"{model_name}.jsonl", "a") as f:
            f.write(
                json.dumps(
                    {
                        "request": request.dict(),
                        "completion": completion.to_dict(),
                        "response": resp,
                    }
                )
                + "\n"
            )
    return resp


def get_evaluate_schema():
    subproperty = {
        "type": "object",
        "properties": {
            "score": {
                "type": "number",
                "description": "The score for the evaluation.",
            },
            "explanation": {
                "type": "string",
                "description": "The explanation for the score.",
            },
        },
        "required": ["score", "explanation"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "quantity": subproperty,
            "quality": subproperty,
            "relation": subproperty,
            "manner": subproperty,
        },
        "required": ["quantity", "quality", "relation", "manner"],
        "additionalProperties": False,
    }


def process_genireval(request: GenIREvalRequest) -> AppEvalRequest:
    idx = request.userTurnIndex

    if idx is None or idx < 0 or idx >= len(request.simulation.userTurns):
        idx = len(request.simulation.userTurns) - 1

    if idx < 0:
        logger.error("Proxy: No user turns found in the simulation.")
        return EvalResponse(
            score=0.0, explanation="No user turns found in the simulation."
        )

    current_turn = request.simulation.userTurns[idx]
    return AppEvalRequest(
        issue=request.simulation.configuration.topic.description,
        argument=current_turn.utterance,
        counter_argument=current_turn.systemResponse.utterance,
    )


# NOTE: this is inelegant, but we need to cache the initial request and the model name
# but the request is not really hashable so we have to use a custom hash function
@cachetools.cached(
    cache=cachetools.LRUCache(maxsize=128),
    key=lambda request, model_name: cachetools.keys.hashkey(
        (process_genireval(request), model_name)
    ),
)
def cached_evaluate(request: GenIREvalRequest, model_name: str) -> EvalResponse:
    app_request = process_genireval(request)
    prompt_template = env.get_template("eval.md.j2")
    prompt = prompt_template.render(
        issue=app_request.issue,
        argument=app_request.argument,
        counter_argument=app_request.counter_argument,
    )
    model_fqn = get_model(model_name)

    for attempt in range(MAX_RETRIES):
        try:
            completion = client.chat.completions.create(
                model=model_fqn,
                messages=[{"role": "user", "content": prompt}],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "EvalResponse",
                        "strict": True,
                        "schema": get_evaluate_schema(),
                    },
                },
            )
            response_content = completion.choices[0].message.content
            eval_response = json.loads(response_content)
            break
        except Exception as e:
            logger.error(
                f"Attempt {attempt + 1}/{MAX_RETRIES}: Error during evaluation for dimension {request.dimension}: {e}"
            )
            if attempt == MAX_RETRIES - 1:  # Last attempt
                return {"error": f"Failed after {MAX_RETRIES} attempts: {str(e)}"}

    if os.environ.get("LOG_PATH"):
        log_path = Path(os.environ.get("LOG_PATH")) / "evaluate"
        log_path.mkdir(parents=True, exist_ok=True)
        with open(log_path / f"{model_name}.jsonl", "a") as f:
            f.write(
                json.dumps(
                    {
                        "request": request.dict(),
                        "completion": completion.to_dict(),
                        "response": eval_response,
                    }
                )
                + "\n"
            )
    return eval_response


@app.post("/evaluate/{model_name}")
async def evaluate(request: GenIREvalRequest, model_name: str) -> EvalResponse:
    return cached_evaluate(request, model_name)


# healthcheck endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}
