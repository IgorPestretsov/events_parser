FROM python:3.10.6

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    DST=/usr/src/app \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.3.1

WORKDIR ${DST}

RUN pip install "poetry==$POETRY_VERSION"

COPY ./poetry.lock ./
COPY ./pyproject.toml ./

RUN poetry install --only main --no-interaction --no-root

COPY ./src/ ${DST}/src



CMD ["python3", "src/main.py"]

