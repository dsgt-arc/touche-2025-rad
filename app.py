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
PROMPT_TEMPLATE = """"### Issue:\n"
    "{issue}\n\n"
    "### Argument:\n"
    "{argument}\n\n"
    "### Counter-argument:\n"
    "{counter_argument}\n\n"
    "### Definition of {dimension_name}:\n"
    "{dimension_definition}\n\n"
    "### Task:\n"
    "Critically evaluate the {dimension_name} of the counter-argument on a scale from 0 (extremely poor) to 1 (exceptional), using increments of 0.01.\n\n"
    "Be highly discerning and rigorous in your assessment:\n"
    "- Actively look for weaknesses, gaps, or areas for improvement.\n"
    "- A score of 1.0 should be reserved for responses that are flawless and could not be improved in any way—this should be extremely rare.\n"
    "- A score of 0.5 means the response is adequate but has clear room for improvement.\n"
    "- Most responses should fall between 0 and 0.8 unless they are truly outstanding.\n"
    "- Justify your score by referencing specific strengths and weaknesses in the counter-argument.\n\n"
    "Format your response as a single JSON object with exactly these keys:\n"
    "- key='explanation': A concise, critical explanation of your score, citing both strengths and weaknesses.\n"
    "- key='score': The score as a number between 0 and 1 (e.g., 0.00, 0.50, 0.79).\n\n"
    "### Example:\n"
    "{{\"explanation\":\"The counter-argument addresses the main point but lacks depth and omits key evidence. Reasoning is mostly sound but could be clearer.\",\"score\":0.62}}\n\n"
    "Your response:\n"
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
