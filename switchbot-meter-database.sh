#!/bin/bash

cd "$(dirname "$0")"

source .venv/bin/activate
set -a
source .env
set +a

uv run -m switchbot_meter_database.main
