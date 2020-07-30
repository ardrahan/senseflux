# SenseFlux

SenseFlux is web services designed to accept data from a [VegeHub](https://www.vegetronix.com/Products/VG-HUB/) Wi-Fi sensor box and ship that data to InfluxDB.

Full Blog Post: Coming Soon

## Quick Start

```bash
docker network create sensenet

docker run --name influx-sf --network sensenet \
   -e INFLUXDB_USER=influx \
   -e INFLUXDB_USER_PASSWORD=1nf1pAss \
   -v influx-state:/var/lib/influxdb \
   influxdb

docker run --name senseflux-sf --network sensenet -p 8003:8003 \
  -e SF_API_KEY=TESTKey \
  -e INFLUXDB_HOST=influx-sf \
  -e INFLUXDB_USERNAME=influx \
  -e INFLUXDB_PASSWORD=1nf1pAss battlepenguin/senseflux:0.0.5

docker run --name chronograf-sf --network sensenet -p 8888:8888 \
  -v chronograf-state:/var/lib/chronograf \
  -e INFLUXDB_URL=http://influx-sf:8086 \
  -e INFLUXDB_USERNAME=influx \
  -e INFLUXDB_PASSWORD=1nf1pAss \
  chronograf
```