from typing import List
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
    userTurns: List[UserTurn]


class EvalRequest(BaseModel):
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
    "quantity": "The counter-argument provides a sufficient amount of information, reasons, and/or evidence for its claims. It adequately addresses the main points of the argument it is responding to.",
    "quality": "The counter-argument presents logical, coherent, and well-reasoned points. The information used is accurate and credible where applicable. The reasoning is sound and persuasive.",
    "relation": "The counter-argument is directly relevant to the argument it is responding to. It stays on topic and clearly addresses the core issues or claims raised in the argument, rather than deflecting or discussing unrelated matters.",
    "manner": "The counter-argument uses clear, grammatically correct, and unambiguous language. It sticks to the main topic and does not make things overly complicated. The tone is appropriate and respectful.",
}
PROMPT_TEMPLATE = """### Issue:
{issue}

### Argument:
{argument}

### Counter-argument:
{counter_argument}

### Definition of {dimension_name}:
{dimension_definition}

### Task:
On a scale from 0 (extremely bad) to 1 (extremely good), how would you rate the {dimension_name} of the counter-argument?

Format your message as only one JSON object with exactly these keys:
- key='explanation': A concise yet descriptive explanation of your score.
- key='score': The score as number between 0 and 1, 0 being extremely bad, and 1 being exceptionally good.

### Example:
{{"explanation":"your explanation","score":0.5}}

Your response:
"""


@app.post("/evaluate")
async def evaluate(request: AppEvalRequest):
    definition = DIMENSION_DEFINITIONS[request.dimension]
    prompt = PROMPT_TEMPLATE.format(
        issue=request.issue,
        argument=request.argument,
        counter_argument=request.counter_argument,
        dimension_name=request.dimension,
        dimension_definition=definition,
    )
    try:
        response = (
            model_client._client.inference(
                model_name=TensorZeroChatResourceModel.GPT4_O_LATEST,
                input={"messages": [{"role": "user", "content": prompt}]},
            )
            .content[0]
            .text
        )
        res = json.loads(response)
        if "score" not in res or "explanation" not in res:
            logger.error(
                f"LLM response for {request.dimension_name} missing 'score' or 'explanation'. Received: {res}"
            )
            raise HTTPException(
                status_code=500,
                detail="LLM response did not contain score and explanation.",
            )

        return {"score": res["score"], "explanation": res["explanation"]}

    except Exception as e:
        return {"error": str(e)}


# healthcheck endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}
