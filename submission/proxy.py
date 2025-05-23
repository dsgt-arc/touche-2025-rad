import os
from typing import List
import requests
import logging
from fastapi import FastAPI
from pydantic import BaseModel

BASE_URL = os.getenv("BASE_URL", "http://app:8500")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Message(BaseModel):
    role: str
    content: str


class Request(BaseModel):
    messages: list[Message]


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


@app.post("/")
async def respond(request: Request):
    resp = requests.post(f"{BASE_URL}/", json=request.dict())
    return resp.json()


async def process_evaluation(request: GenIREvalRequest, dimension_name: str):
    target_url = f"{BASE_URL}/evaluate"
    idx = request.userTurnIndex

    if idx is None or idx < 0 or idx >= len(request.simulation.userTurns):
        idx = len(request.simulation.userTurns)

    if idx < 0:
        logger.error("Proxy: No user turns found in the simulation.")
        return EvalResponse(
            score=0.0, explanation="No user turns found in the simulation."
        )

    current_turn = request.simulation.userTurns[idx]
    app_payload = AppEvalRequest(
        dimension_name=dimension_name,
        issue=request.simulation.configuration.topic.description,
        argument=current_turn.utterance,
        counter_argument=current_turn.systemResponse.utterance,
    )

    logger.info(
        f"Proxy: Sending {dimension_name} evaluation to {target_url} with payload: {app_payload.dict()}"
    )
    resp = requests.post(target_url, json=app_payload.dict())
    logger.info(
        f"Proxy: Received status {resp.status_code} from {target_url} for {dimension_name} evaluation"
    )
    return resp.json()


@app.post("/quantity")
async def quantity(request: GenIREvalRequest):
    return await process_evaluation(request, "quantity")


@app.post("/quality")
async def quality(request: GenIREvalRequest):
    return await process_evaluation(request, "quality")


@app.post("/manner")
async def manner(request: GenIREvalRequest):
    return await process_evaluation(request, "manner")


@app.post("/relation")
async def relation(request: GenIREvalRequest):
    return await process_evaluation(request, "relation")
