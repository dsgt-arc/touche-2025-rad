#!/bin/bash

# TODO add base images to repo that include the evals images

MODEL=${1?model is required}

docker run --rm -it \
  --volume $PWD:/data \
  --entrypoint /genirsim/run.sh \
  $MODEL-evals \
  --evaluate-run-file=/data/simulations/$MODEL-simulation.jsonl \
  --output-file=/data/evals/$MODEL.jsonl
