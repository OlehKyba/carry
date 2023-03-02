FROM python:3.11-alpine AS venv

ENV POETRY_VERSION=1.4.0

RUN pip install "poetry==$POETRY_VERSION"
WORKDIR /app
COPY ./poetry.lock ./pyproject.toml ./

RUN python -m venv --copies /app/venv
RUN . /app/venv/bin/activate && poetry install --no-root --only main

FROM python:3.11-alpine as base

COPY --from=venv /app/venv /app/venv/
ENV PATH /app/venv/bin:$PATH

WORKDIR /app
COPY ./carry /app/carry
COPY ./settings.toml ./.secrets.toml /app/

FROM base as dev

ENV ENV_FOR_DYNACONF "development"

FROM base as prd

ENV ENV_FOR_DYNACONF "production"
