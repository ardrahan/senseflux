# SenseFlux

SenseFlux is web services designed to accept data from a [VegeHub](https://www.vegetronix.com/Products/VG-HUB/) Wi-Fi sensor box and ship that data to InfluxDB.

Full Blog Post: https://battlepenguin.com/tech/plants-and-soil-sensors/

2021/10/10 by ardrahan
-updated to use influxdb 2
-updated vegehub json to work with what my vegehub sent
-updated soil moisture to use piecewise linear curve approximation

## Configuration

You may use command line arguments or environment variables.

| Command Line Option | Environment Variable | Default | Description |
|-|-|-|-|
| --port | SF_PORT | 8003 | Web Service Port |
| --api-key | SF_API_KEY | |
| --influxdb-host | INFLUXDB_URL | http://localhost:8086 | Influx Server URL |
| --influxdb-port | INFLUXDB_ORG | Senseflux | Influx Org |
| --influxdb-database | INFLUXDB_DATABASE | senseflux | Influx Bucket |
| --influxdb-username | INFLUXDB_TOKEN | |
| --field1 | FIELD1 | SoilMoisture |
| --field2 | FIELD2 | Voltage |
| --field3 | FIELD3 | Voltage |
| --field4 | FIELD4 | Voltage |
| --field5 | FIELD5 | Voltage |

## Quick Start

```bash
docker network create sensenet

docker run -d --name influx-sf --network sensenet \
   -e INFLUXDB_USER=influx \
   -e INFLUXDB_USER_PASSWORD=1nf1pAss \
   -v influx-state:/var/lib/influxdb \
   influxdb

docker run -d --name senseflux-sf --network sensenet -p 8003:8003 \
  -e SF_API_KEY=TESTKey \
  -e INFLUXDB_HOST=influx-sf \
  -e INFLUXDB_USERNAME=influx \
  -e INFLUXDB_PASSWORD=1nf1pAss \
  -e FIELD1=Humidity \
  -e FIELD2=SoilTemperature \
  -e FIELD3=SoilMoisture \
  -e FIELD4=Darkness \
  -e FIELD5=Battery \
  battlepenguin/senseflux:v0.0.9

docker run --name chronograf-sf --network sensenet -p 8888:8888 \
  -v chronograf-state:/var/lib/chronograf \
  -e INFLUXDB_URL=http://influx-sf:8086 \
  -e INFLUXDB_USERNAME=influx \
  -e INFLUXDB_PASSWORD=1nf1pAss \
  chronograf
```

## Testing

If you don't have a real VegeHub, or are developing locally, you can test your service like so.

```
curl -X POST localhost:8003/create/vghub --header "Content-Type: application/json" --data "{\"write_api_key\":\"TESTKey\", \"channel_id\":\"LocalTest\", \"updates\":[{\"created_at\":\"$(date -u "+%Y-%m-%d %H:%M:%S")\",\"field1\":1.827,\"field2\":1.541,\"field3\":0.077,\"field4\":1.905}]}"
```

## Limitations

* SenseFlux does not allow different field configurations for each Wi-Fi Hub
* Multiple Wi-Fi hubs can send to SenseFlux with different channel IDs, but they must have the same sensors in the same order
