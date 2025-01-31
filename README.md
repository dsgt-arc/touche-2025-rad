# touche2025-rad

## quickstart

### installing pre-commit

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

This will then run linting and formatting checks before each commit.

### updating requirements

To update the requirements file, install `uv` for `pip compile`.

```bash
pip install uv
uv pip compile requirements.in > requirements.txt
```

We use the compiled requirements file only to install the package in docker.

### building the docker image

Update the requirements file and then build the image.

```bash
docker compose build
```

Run the image in a container:

```bash
docker compose run app bash
```

### running tests

In the docker container, run the pytest command:

```bash
pytest
```
