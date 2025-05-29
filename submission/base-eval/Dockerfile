ARG BASE_IMAGE_VERSION=0.4.0

FROM ghcr.io/touche-webis-de/touche25-retrieval-augmented-debating-evaluation-1-baseline-py

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY start.sh proxy.py ./

ARG BASE_URL=https://touche-2025-rad.dsgt-kaggle.org/api
ARG MODEL_NAME=gemini-2.5-flash-preview-05-20
ENV BASE_URL=${BASE_URL}
ENV MODEL_NAME=${MODEL_NAME}
