import logging
import os
from typing import Any, List

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

BASE_URL = os.getenv("BASE_URL", "http://app:8500")
MODEL_NAME = os.environ["MODEL_NAME"]
# MAX_RETRIES = 5 # Retries removed
# RETRY_DELAY_SECONDS = 1 # Retries removed
REQUEST_TIMEOUT_SECONDS = 60

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
    resp = None  # Initialize resp to None
    logger.info(f"Attempting to call {target_url} for dimension '{dimension_name}'")
    try:
        resp = requests.post(
            target_url, json=request.dict(), timeout=REQUEST_TIMEOUT_SECONDS
        )
        resp.raise_for_status()  # Raises HTTPError for 4XX/5XX responses
        response_json = resp.json()

        if dimension_name not in response_json:
            logger.error(
                f"Dimension '{dimension_name}' not found in successful (status {resp.status_code}) response from {target_url}. "
                f"Keys: {list(response_json.keys())}. Response snippet: {str(response_json)[:500]}"
            )
            # This is a contract violation from the downstream service.
            raise HTTPException(
                status_code=502,  # Bad Gateway: proxy received an invalid response
                detail=f"Evaluation service returned unexpected structure: dimension '{dimension_name}' missing.",
            )

        return EvalResponse(**(response_json[dimension_name]))

    except requests.exceptions.Timeout as e:
        logger.error(
            f"Call to {target_url} (dimension: {dimension_name}) timed out after {REQUEST_TIMEOUT_SECONDS}s: {e}"
        )
        raise HTTPException(
            status_code=504,  # Gateway Timeout
            detail=f"Evaluation service timed out for dimension '{dimension_name}'.",
        ) from e
    except requests.exceptions.ConnectionError as e:
        logger.error(
            f"Call to {target_url} (dimension: {dimension_name}) failed due to a connection error: {e}"
        )
        raise HTTPException(
            status_code=503,  # Service Unavailable
            detail=f"Evaluation service connection failed for dimension '{dimension_name}'.",
        ) from e
    except (
        requests.exceptions.HTTPError
    ) as e:  # Handles 4xx/5xx from resp.raise_for_status()
        logger.error(
            f"Call to {target_url} (dimension: {dimension_name}) failed with HTTP status {e.response.status_code}: {e}"
        )
        if resp is not None:
            logger.error(
                f"Downstream response (status {resp.status_code}): {resp.text[:500]}..."
            )
        raise HTTPException(
            status_code=502,  # Bad Gateway
            detail=f"Evaluation service returned an error for dimension '{dimension_name}': {e.response.status_code} - {e.response.reason}",
        ) from e
    except requests.exceptions.JSONDecodeError as e:
        logger.error(
            f"Failed to decode JSON response from {target_url} (dimension: {dimension_name}). Status: {resp.status_code if resp else 'N/A'}. Response text: {resp.text[:500] if resp else 'N/A'}... Error: {e}"
        )
        raise HTTPException(
            status_code=502,  # Bad Gateway
            detail=f"Invalid JSON response from evaluation service for dimension '{dimension_name}'.",
        ) from e


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
