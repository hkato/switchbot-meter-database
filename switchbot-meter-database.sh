#!/bin/bash

cd "$(dirname "$0")"

source .venv/bin/activate
set -a
source .env
set +a

switchbot-meter-database
