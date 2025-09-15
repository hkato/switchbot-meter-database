#!/bin/bash

mkdir -p lambda_layer
uv export --format requirements-txt --no-dev --no-hashes > lambda_layer/requirements.txt

sam build --use-container

sam deploy
