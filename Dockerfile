FROM python:3.11 as builder

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# COPY source
COPY . /build/switchbot-influxdb
WORKDIR /build/switchbot-influxdb

# Build package
RUN "$HOME"/.local/bin/poetry build

FROM python:3.11-slim

# Install package
COPY --from=builder /build/switchbot-influxdb/dist/switchbot_influxdb-*.whl /tmp
RUN pip install --no-cache-dir /tmp/switchbot_influxdb-*.whl

ENTRYPOINT [ "switchbot-influxdb", "-d" ]
