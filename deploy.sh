#!/bin/bash

sam build

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
