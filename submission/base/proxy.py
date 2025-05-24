import logging
import os
from typing import Any, List

import requests
from fastapi import FastAPI
from pydantic import BaseModel

BASE_URL = os.getenv("BASE_URL", "http://app:8500")
MODEL_NAME = os.environ["MODEL_NAME"]
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Message(BaseModel):
    role: str
    content: str


class Request(BaseModel):
    messages: list[Message]


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


class EvalResponse(BaseModel):
    score: float
    explanation: str


app = FastAPI()


@app.post("/")
async def respond(request: Request):
    resp = requests.post(f"{BASE_URL}/respond/{MODEL_NAME}", json=request.dict())
    return resp.json()


async def process_evaluation(
    request: GenIREvalRequest, dimension_name: str
) -> EvalResponse:
    target_url = f"{BASE_URL}/evaluate/{MODEL_NAME}"
    logger.info(
        f"Proxy: Sending {dimension_name} evaluation to {target_url} with payload: {request.dict()}"
    )
    resp = requests.post(target_url, json=request.dict())
    logger.info(
        f"Proxy: Received status {resp.status_code} from {target_url} for {dimension_name} evaluation"
    )
    return EvalResponse(**(resp.json()[dimension_name]))


@app.post("/quantity")
async def quantity(request: GenIREvalRequest) -> EvalResponse:
    return await process_evaluation(request, "quantity")


@app.post("/quality")
async def quality(request: GenIREvalRequest) -> EvalResponse:
    return await process_evaluation(request, "quality")


@app.post("/manner")
async def manner(request: GenIREvalRequest) -> EvalResponse:
    return await process_evaluation(request, "manner")


@app.post("/relation")
async def relation(request: GenIREvalRequest) -> EvalResponse:
    return await process_evaluation(request, "relation")
