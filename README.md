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

### running the app

Use docker compose to run the app:

```bash
docker compose up
```

Alternatively:

```bash
docker compose run --service-ports app streamlit run app.py
```

If you are on your bare system, install all the python dependencies:

```bash
pip install uv
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Install the package itself in editable mode:

```bash
uv pip install -e .
```

Then run the app:

```bash
streamlit run app.py
```
