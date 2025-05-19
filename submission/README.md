# submission

This is a simple proxy to the rest of the services.

## How to run the local submission

To compile dependencies:

```bash
uv pip compile pyproject.toml > requirements.txt
```

To run the services:

```bash
docker compose build
docker compose up
```

Then you can run the gensimir interface on port 8000.
Use the sample-conf.json to get a locally running version of the service.

## How to run the submission

Do the tira things:

```bash
uv tool install tira
```

Run the `tira-cli login` command as per the instructions in the tira submission page for docker.

```bash
tira-cli code-submission \
    --path . \
    --task retrieval-augmented-debating-2025 \
    --dataset rad25-2025-01-16-toy-20250116-training \
    --command '/genirsim/run.sh         --configuration-file=$inputDataset/*.json --parameter-file=$inputDataset/*.tsv --output-file=$outputDir/simulations.jsonl' \
    --allow-network \
    --dry-run
```

This is not quite the docker submission, but we're not doing anything more complex than the default submission if we can assume that requests is in the environment.
