import click
from influxdb import InfluxDBClient
from waitress import serve
import logging

from senseflux.webapp import create_app

console = logging.StreamHandler()
console.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
log = logging.getLogger("senseflux")
log.addHandler(console)
log.setLevel(logging.DEBUG)


@click.command()
@click.option('--port', envvar='SF_PORT', default=8003, help='Web Service Port')
@click.option('--api-key', envvar='SF_API_KEY', default=None)
@click.option('--influxdb-host', envvar='INFLUXDB_HOST', default='localhost', help='Influx Server hostname')
@click.option('--influxdb-port', envvar='INFLUXDB_PORT', default=8086, help='Influx Server port')
@click.option('--influxdb-database', envvar='INFLUXDB_DATABASE', default='senseflux')
@click.option('--influxdb-username', envvar='INFLUXDB_USERNAME', default=None)
@click.option('--influxdb-password', envvar='INFLUXDB_PASSWORD', default=None)
def main(port, api_key, influxdb_host, influxdb_port, influxdb_database, influxdb_username, influxdb_password):
    if influxdb_username and influxdb_password:
        influxdb_client = InfluxDBClient(host=influxdb_host, port=influxdb_port,
                                         username=influxdb_username, password=influxdb_password)
    else:
        influxdb_client = InfluxDBClient(host=influxdb_host, port=influxdb_port)
    influxdb_client.create_database(influxdb_database)
    influxdb_client.switch_database(influxdb_database)
    log.info(f'Influx Host: {influxdb_host}:{influxdb_port}')
    log.info(f'Influx User: {influxdb_username}')
    log.info(f'Influx Database {influxdb_database}')

    app = create_app(influxdb_client, influxdb_database, api_key)
    log.info(f'Starting senseflux on port {port}')
    serve(app, listen=f'*:{port}')


if __name__ == '__main__':
    main()
