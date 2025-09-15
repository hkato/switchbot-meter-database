#!/bin/bash

mkdir -p lambda_layer
uv export --format requirements-txt --no-dev --no-hashes > lambda_layer/requirements.txt

sam build --use-container

set -a
source .env
set +a

sam deploy \
    --parameter-overrides \
    Database="$DATABASE" \
    SwitchbotToken="$SWITCHBOT_TOKEN" \
    SwitchbotSecret="$SWITCHBOT_SECRET" \
    MongoDBUri="$MONGODB_URI" \
    MongoDBDatabase="$MONGODB_DATABASE" \
    MongoDBCollection="$MONGODB_COLLECTION" \
    MongoDBUsername="$MONGODB_USERNAME" \
    MongoDBPassword="$MONGODB_PASSWORD"
