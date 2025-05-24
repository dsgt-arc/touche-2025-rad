from typing import List, Any
import os
from jinja2 import Environment, PackageLoader, select_autoescape
from openai import OpenAI
import yaml
from pathlib import Path
import json
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from touche_rad.ai.elasticsearch_retriever import ElasticsearchRetriever

load_dotenv()
env = Environment(loader=PackageLoader("app"), autoescape=select_autoescape())

# google/gemini-2.5-flash-preview-05-20
# openai/gpt-4o
# openai/gpt-4.1
# anthropic/claude-sonnet-4
# google/gemini-2.5-pro-preview
MODEL = os.getenv("MODEL", "google/gemini-2.5-pro-preview")
SYSTEM = os.getenv("SYSTEM", "dev")
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
    dimension: str
    issue: str
    argument: str
    counter_argument: str


class EvalResponse(BaseModel):
    score: float
    explanation: str


app = FastAPI()

retriever = ElasticsearchRetriever()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


@app.post("/")
async def respond(request: Request):
    # get the message for user and assistant
    # we're given some odd number of messages that need to be placed into the context appropriately
    print(request)
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

    completion = client.chat.completions.create(
        model=MODEL,
        messages=request.messages
        + [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    content = completion.choices[0].message.content
    resp = {"content": content, "arguments": evidence}

    if os.environ.get("LOG_PATH"):
        log_path = Path(os.environ.get("LOG_PATH"))
        log_path.mkdir(parents=True, exist_ok=True)
        # jsonl
        with open(log_path / "log.jsonl", "a") as f:
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


DIMENSION_DEFINITIONS = {
    "quantity": "The counter-argument provides enough relevant information, reasons, and evidence to support its claims. It addresses all major points raised in the original argument, leaving no significant gaps.",
    "quality": "The counter-argument uses logical, coherent, and well-structured reasoning. Its claims are accurate, credible, and well-supported by appropriate evidence. The argument is persuasive and free from logical fallacies.",
    "relation": "The counter-argument is directly relevant to the original argument. It responds specifically to the main issues or claims, without digressing or introducing unrelated topics.",
    "manner": "The counter-argument is expressed clearly and unambiguously, using correct grammar and appropriate language. It maintains a respectful tone and avoids unnecessary complexity or confusion.",
}


@app.post("/evaluate")
async def evaluate(request: AppEvalRequest):
    MAX_RETRIES = 5
    definition = DIMENSION_DEFINITIONS[request.dimension]
    prompt_template = env.get_template("eval.md.j2")
    prompt = prompt_template.render(
        issue=request.issue,
        argument=request.argument,
        counter_argument=request.counter_argument,
        dimension_name=request.dimension,
        dimension_definition=definition,
    )

    for attempt in range(MAX_RETRIES):
        try:
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            response_content = completion.choices[0].message.content
            res = json.loads(response_content)

            if "score" not in res or "explanation" not in res:
                logger.warning(
                    f"Attempt {attempt + 1}/{MAX_RETRIES}: LLM response for {request.dimension} missing 'score' or 'explanation'. Received: {res}"
                )
                if attempt == MAX_RETRIES - 1:
                    raise HTTPException(
                        status_code=500,
                        detail="LLM response did not contain score and explanation after multiple retries.",
                    )
                continue

            eval_response = {"score": res["score"], "explanation": res["explanation"]}

            if os.environ.get("LOG_PATH"):
                log_path = Path(os.environ.get("LOG_PATH"))
                log_path.mkdir(parents=True, exist_ok=True)
                with open(log_path / "eval-log.jsonl", "a") as f:
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

        except Exception as e:
            logger.error(
                f"Attempt {attempt + 1}/{MAX_RETRIES}: Error during evaluation for dimension {request.dimension}: {e}"
            )
            if attempt == MAX_RETRIES - 1:  # Last attempt
                return {"error": f"Failed after {MAX_RETRIES} attempts: {str(e)}"}

    return {
        "error": f"Evaluation failed for dimension {request.dimension} after {MAX_RETRIES} attempts."
    }


# healthcheck endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}
