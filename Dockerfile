FROM python:3.12

RUN apt-get -y update && \
     apt-get -y install default-jre

WORKDIR /app
RUN pip install --upgrade pip
COPY requirements.txt pyproject.toml /app/
RUN pip install -r requirements.txt

COPY . /app
RUN pip install -e .
