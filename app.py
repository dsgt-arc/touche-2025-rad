from typing import List
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from touche_rad.ai.elasticsearch_retriever import ElasticsearchRetriever
from touche_rad.ai.tensorzero import TensorZeroClient
from touche_rad.core.context import DebateContext
from touche_rad.core.machine import DebateMachine
from touche_rad.core.rag_pipeline import RAGDebater
from touche_rad.core.strategy.drivers.rag import RAGStrategy

load_dotenv()


class Message(BaseModel):
    role: str
    content: str


class Request(BaseModel):
    messages: List[Message]


app = FastAPI()

retriever = ElasticsearchRetriever()
model_client = TensorZeroClient(
    base_url=os.getenv("TENSORZERO_GATEWAY_URL", "http://localhost:3000")
)
rag_debater = RAGDebater(retriever, model_client)
strategy = RAGStrategy(rag_debater, retrieval_mode="text")


@app.post("/")
async def respond(request: Request):
    # get the message for user and assistant
    # we're given some odd number of messages that need to be placed into the context appropriately
    user_messages = [msg.content for msg in request.messages if msg.role == "user"]
    assistant_messages = [
        msg.content for msg in request.messages if msg.role == "assistant"
    ]

    context = DebateContext(
        client=model_client,
        user_utterances=user_messages,
        system_utterances=assistant_messages,
        current_turn=len(user_messages),
        max_turns=5,
    )
    _ = DebateMachine(model=context)

    # NOTE: this has been rewritten return a tuple of content and evidence for the RAG strategy
    content, evidence = strategy.generate_response(context)
    return {"content": content, "arguments": evidence}


# healthcheck endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}
