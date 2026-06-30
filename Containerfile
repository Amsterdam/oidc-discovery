ARG PYTHON_VERSION
FROM ghcr.io/astral-sh/uv:0.11-python${PYTHON_VERSION:-3.11}-trixie-slim

RUN set -eux; \
    apt-get update; \
    apt-get install git -yq; \
    apt-get clean;

RUN uv python install ${PYTHON_VERSION:-3.11}

WORKDIR /app

ADD . /app

RUN uv sync --locked

ENTRYPOINT ["/app/entrypoint.sh"]
