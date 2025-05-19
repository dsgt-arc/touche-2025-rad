#!/bin/bash

cd $(dirname $0)
fastapi run --port 8080 main.py
