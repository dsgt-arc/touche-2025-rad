#!/bin/bash

MODEL=${1?model is required}
PARAMFILE=${2?paramfile is required}

docker run --rm -it \
  --volume $PWD:/data \
  --entrypoint /genirsim/run.sh \
  $MODEL \
  --parameter-file=/data/data/$PARAMFILE.tsv --output-file=/data/data/$MODEL-simulation.jsonl
