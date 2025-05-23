from typing import Any, List
import os
from jinja2 import Environment, PackageLoader, select_autoescape
from openai import OpenAI
import yaml
from pathlib import Path
import json

from dotenv import load_dotenv
from fastapi import FastAPI
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


class Message(BaseModel):
    role: str
    content: str


class Request(BaseModel):
    messages: List[Message]


# class EvalRequest(BaseModel):
#     model: str
#     keep_alive: str
#     messages: List[Message]


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


@app.post("/evaluate")
async def evaluate(request: Any):
    response = model_client._client.inference(
        model_name=TensorZeroChatResourceModel.GPT4_O_LATEST,
        input={"messages": [{"role": request.role, "content": request.content}]},
    )
    return {"message": {"content": response.content[0].text}}


# healthcheck endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}
