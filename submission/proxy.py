import os

import requests
from fastapi import FastAPI
from pydantic import BaseModel

BASE_URL = os.getenv("BASE_URL", "http://app:8500")


class Message(BaseModel):
    role: str
    content: str


class Request(BaseModel):
    messages: list[Message]


app = FastAPI()


@app.post("/")
async def respond(request: Request):
    resp = requests.post(f"{BASE_URL}/", json=request.dict())
    return resp.json()
