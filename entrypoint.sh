#!/usr/bin/env bash
set -eux

uv sync --locked

exec "$@"
