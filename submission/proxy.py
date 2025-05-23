import os
from typing import Any
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


# class EvalRequest(BaseModel):
#     model: str
#     keep_alive: str
#     messages: List[Message]


app = FastAPI()


@app.post("/")
async def respond(request: Request):
    resp = requests.post(f"{BASE_URL}/", json=request.dict())
    return resp.json()


@app.post("/evaluate")
async def evaluate(request: Any):
    target_url = f"{BASE_URL}/evaluate"
    payload = request.dict()
    logger.info(f"Proxy: Sending POST to {target_url} with payload: {payload}")
    resp = requests.post(target_url, json=payload)
    logger.info(f"Proxy: Received status {resp.status_code} from {target_url}")
    if resp.status_code >= 400:
        try:
            logger.error(f"Proxy: Error response body from {target_url}: {resp.json()}")
        except requests.exceptions.JSONDecodeError:
            logger.error(
                f"Proxy: Error response body (not JSON) from {target_url}: {resp.text}"
            )
    return resp.json()
