# SwitchBot-InfluxDB

Write SwitchBot environmental sensor data to InfluxDB

## Overview

![Overview](images/overview.png)

## Supported devices

| name                    | deviceType | remarks    |
|-------------------------|------------|------------|
| SwitchBot Meter         | Meter      | not tested |
| SwitchBot Meter Plus    | MeterPlus  | not tested |
| SwitchBot Outdoor Meter | WoIOSensor | not tested |
| SwitchBot Humidifier    | Humidifier | not tested |
| SwitchBot Hub 2         | Hub 2      | tested     |

## Usage

Set environmental variables

```sh
export SWITCHBOT_ACCESS_TOKEN=your_switchbot_token
export SWITCHBOT_SECRET=your_switchbot_secret
export INFLUXDB_URL=http://influxdb:8086
export INFLUXDB_ORG=your_org
export INFLUXDB_BUCKET=your_bucket
export INFLUXDB_TOKEN=your_influxdb_token
```

Run as daemon

```sh
switchbot-influx -d
```

or command line options

```sh
switchbot-influxdb --help

usage: switchbot-influxdb [-h] [-d] [-t TIME] [--url URL] [--token TOKEN] [--org ORG] [--bucket BUCKET] [--switchbot-token SWITCHBOT_TOKEN] [--switchbot-secret SWITCHBOT_SECRET]

options:
  -h, --help            show this help message and exit
  -d, --daemon          Daemon mode
  -t TIME, --time TIME  Time interval
  --url URL             InfluxDB URL
  --token TOKEN         InfluxDB token
  --org ORG             InfluxDB organization
  --bucket BUCKET       InfluxDB bucket
  --switchbot-token SWITCHBOT_TOKEN
                        SwitchBot token
  --switchbot-secret SWITCHBOT_SECRET
                        SwitchBot secret

```

```sh
$ switchbot-influxdb -d \
    --url http://influxdb:8086 --org your_org --bucket your_bucket --token your_token \
    --switchbot-token your_token --switchbot-secret your_secret
```

Log messages

```sh
[INFO    ] 2024-07-03 20:01:26,955 main Start
[INFO    ] 2024-07-03 20:01:29,249 main Meter devices: {'XXXXXXXXXXXX': 'Hub 2'}
[INFO    ] 2024-07-03 20:01:33,373 task Saved: {'device_id': 'XXXXXXXXXXXX', 'device_type': 'hub2', 'hub_device_id': 'XXXXXXXXXXXX', 'humidity': 66, 'temperature': '28.2', 'light_level': 12, 'version': 'V1.0-1.1'}
[INFO    ] 2024-07-03 20:06:33,433 task Saved: {'device_id': 'XXXXXXXXXXXX', 'device_type': 'hub2', 'hub_device_id': 'XXXXXXXXXXXX', 'humidity': 66, 'temperature': '28.2', 'light_level': 12, 'version': 'V1.0-1.1'}
...
```

## Docker usage

### Create and update .env file

```sh
cp .env.example .env
vi .env
```

### Start SwitchBot-InfluxDB service

```sh
docker compose build
docker compose up -d && docker compose logs -f
```

## Grafana Influx query

```sql
from(bucket: "switchbot")    // your_bucket
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_field"] == "temperature")
```

![Grafana](images/grafana-influx-switchbot.png)
