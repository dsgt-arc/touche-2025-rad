#!/usr/bin/env bash
# usage: ./submit-debate.sh <model> [--dry-run]
WORKDIR=$(dirname "$0")
MODEL=${1?model is required}

docker compose build
cd $WORKDIR/$MODEL
echo $(pwd)
set -x
tira-cli \
    code-submission \
    --path ./ \
    --task retrieval-augmented-debating-2025 \
    --dataset rad25-2025-01-16-toy-20250116-training \
    --command '/genirsim/run.sh --configuration-file=$inputDataset/*.json --parameter-file=$inputDataset/*.tsv --output-file=$outputDir/simulations.jsonl' \
    --allow-network \
    ${2:-}
