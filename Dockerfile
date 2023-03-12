FROM python:3.11-alpine AS venv

ARG INSTALL_DEV=false
ENV POETRY_VERSION=1.4.0

RUN pip install "poetry==$POETRY_VERSION"
WORKDIR /app
COPY ./poetry.lock ./pyproject.toml ./

RUN python -m venv --copies /app/venv
RUN . /app/venv/bin/activate && if [ $INSTALL_DEV == 'true' ]; then poetry install --no-root; else poetry install --no-root --only main; fi

FROM python:3.11-alpine as base

COPY --from=venv /app/venv /app/venv/
ENV PATH /app/venv/bin:$PATH

WORKDIR /app
COPY ./carry /app/carry
COPY ./settings.toml ./.secrets.toml* /app/

FROM base as dev

ENV ENV_FOR_DYNACONF "development"

FROM base as prd

ENV ENV_FOR_DYNACONF "production"
