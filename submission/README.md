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

```bash
# Request the API in a different terminal
curl -X POST -H "Content-Type: application/json" -d '{
  "messages": [
    {"role":"user","content":"I think that it is always wrong to lie since the ten commandments tell us so."},
    {"role":"assistant","content":"I actually think there is a strong case to be made for the idea that \"There is nothing inherently morally wrong about lying.\" In certain situations, like protecting someones life or preventing harm, lying might be seen as a morally justifiable action."},
    {"role":"user","content":"But \"preventing harm\" is a slippery slope."}
  ]
}' http://localhost:8080

{
  "content": "The \"slippery slope\" is not always a fallacy.",
  "arguments": [
    {
      "id": "15978.994",
      "topic": "Should the use of 'chosen' or gender-neutral pronouns be mandatory?",
      "tags": [
        "Politics",
        "Science",
        "Society",
        "Health",
        "Ethics",
        "Gender"
      ],
      "attacks": "The \"slippery slope\" is a logical fallacy.",
      "supports": "The \"slippery slope\" is a logical fallacy.",
      "text": "The \"slippery slope\" is not always a fallacy.",
      "references": [
        "https://en.wikipedia.org/wiki/Slippery_slope#Non-fallacious_usage"
      ],
      "original": "attacks",
      "key": 1,
      "score": 22.987284
    }
  ]
}
```

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
