import os
from typing import List

import requests
from fastapi import FastAPI
from pydantic import BaseModel

BASE_URL = os.getenv("BASE_URL", "http://app:8500")


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


class EvalRequest(BaseModel):
    simulation: Simulation
    userTurnIndex: int | None = None


app = FastAPI()


@app.post("/")
async def respond(request: Request):
    resp = requests.post(f"{BASE_URL}/", json=request.dict())
    return resp.json()


@app.post("/quantity")
async def quantity(request: EvalRequest):
    resp = requests.post(f"{BASE_URL}/quantity", json=request.dict())
    return resp.json()


@app.post("/quality")
async def quality(request: EvalRequest):
    resp = requests.post(f"{BASE_URL}/quality", json=request.dict())
    return resp.json()


@app.post("/relation")
async def relation(request: EvalRequest):
    resp = requests.post(f"{BASE_URL}/relation", json=request.dict())
    return resp.json()


@app.post("/manner")
async def manner(request: EvalRequest):
    resp = requests.post(f"{BASE_URL}/manner", json=request.dict())
    return resp.json()
