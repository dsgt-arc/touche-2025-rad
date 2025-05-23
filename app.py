from typing import List
import os
from jinja2 import Environment, PackageLoader, select_autoescape
from openai import OpenAI
import yaml

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from touche_rad.ai.elasticsearch_retriever import ElasticsearchRetriever
from typing import Optional

load_dotenv()
env = Environment(loader=PackageLoader("app"), autoescape=select_autoescape())


class Message(BaseModel):
    role: str
    content: str


class Request(BaseModel):
    messages: List[Message]
    model: Optional[str] = "openai/gpt-4o"


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
        model=request.model,
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
    return resp


# healthcheck endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}
