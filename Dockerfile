FROM python:3.12

RUN apt-get -y update && \
     apt-get -y install default-jre

WORKDIR /app
ENV UV_SYSTEM_PYTHON=1
RUN pip install --upgrade pip uv
COPY requirements.txt pyproject.toml /app/
RUN uv pip install -r requirements.txt

COPY . /app
RUN uv pip install -e .
