# SwitchBot Meter - InfluxDB

Write SwitchBot environmental sensor data to InfluxDB

## Overview

![Overview](images/overview.png)

## Supported devices

| name                    | deviceType | remarks    |
|-------------------------|------------|------------|
| SwitchBot Meter         | Meter      |            |
| SwitchBot Meter Plus    | MeterPlus  | not tested |
| SwitchBot Outdoor Meter | WoIOSensor | not tested |
| SwitchBot Humidifier    | Humidifier | not tested |
| SwitchBot Hub 2         | Hub 2      |            |

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
switchbot-meter-influx -d
```

or command line options

```sh
switchbot-meter-influxdb --help

usage: switchbot-meter-influxdb [-h] [-d] [-t TIME] [--url URL] [--token TOKEN] [--org ORG] [--bucket BUCKET] [--switchbot-token SWITCHBOT_TOKEN] [--switchbot-secret SWITCHBOT_SECRET]

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
$ switchbot-meter-influxdb -d \
    --url http://influxdb:8086 --org your_org --bucket your_bucket --token your_token \
    --switchbot-token your_token --switchbot-secret your_secret
```

Log messages

```sh
[INFO    ] 2024-07-06 18:02:11,860 main Start
[INFO    ] 2024-07-06 18:02:14,159 main Meter devices: {'XXXXXXXXXXXX': 'Meter', 'YYYYYYYYYYYY': 'Hub 2', 'ZZZZZZZZZZZZ': 'Meter'}
[INFO    ] 2024-07-06 18:02:17,845 task Saved: {'device_id': 'XXXXXXXXXXXX', 'device_type': 'meter', 'hub_device_id': 'YYYYYYYYYYYY', 'humidity': 59, 'temperature': '27.8', 'version': 'V2.5', 'battery': 100}
[INFO    ] 2024-07-06 18:02:20,848 task Saved: {'device_id': 'YYYYYYYYYYYY', 'device_type': 'hub2', 'hub_device_id': 'YYYYYYYYYYYY', 'humidity': 60, 'temperature': '28.5', 'light_level': 13, 'version': 'V1.0-1.1'}
[INFO    ] 2024-07-06 18:02:24,181 task Saved: {'device_id': 'ZZZZZZZZZZZZ', 'device_type': 'meter', 'hub_device_id': 'YYYYYYYYYYYY', 'humidity': 58, 'temperature': '28.1', 'version': 'V2.5', 'battery': 78}
[INFO    ] 2024-07-06 18:07:28,564 task Saved: {'device_id': 'XXXXXXXXXXXX', 'device_type': 'meter', 'hub_device_id': 'YYYYYYYYYYYY', 'humidity': 59, 'temperature': '27.8', 'version': 'V2.5', 'battery': 100}
[INFO    ] 2024-07-06 18:07:31,827 task Saved: {'device_id': 'YYYYYYYYYYYY', 'device_type': 'hub2', 'hub_device_id': 'YYYYYYYYYYYY', 'humidity': 60, 'temperature': '28.5', 'light_level': 13, 'version': 'V1.0-1.1'}
[INFO    ] 2024-07-06 18:07:35,313 task Saved: {'device_id': 'ZZZZZZZZZZZZ', 'device_type': 'meter', 'hub_device_id': 'YYYYYYYYYYYY', 'humidity': 58, 'temperature': '28.1', 'version': 'V2.5', 'battery': 78}
...
```

## Docker usage

### Create and update .env file

```sh
cp .env.example .env
vi .env
```

### Start SwitchBot-Meter-InfluxDB service

```sh
docker compose build
docker compose up -d && docker compose logs -f
```

## Grafana Influx query

```sql
from(bucket: "switchbot")    // your_bucket
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_field"] == "temperature")    // or humidity
```

![Grafana](images/grafana-influx-switchbot.png)
