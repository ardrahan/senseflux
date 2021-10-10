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
@click.option('--influxdb-url', envvar='INFLUXDB_URL', default='Http://localhost:8086', help='Influx Server URL')
@click.option('--influxdb-org', envvar='INFLUXDB_ORG', default='Senseflux')
@click.option('--influxdb-database', envvar='INFLUXDB_DATABASE', default='senseflux')
@click.option('--influxdb-token', envvar='INFLUXDB_TOKEN', default=None)
@click.option('--field1', envvar='FIELD1', default='Voltage')
@click.option('--field2', envvar='FIELD2', default='Voltage')
@click.option('--field3', envvar='FIELD3', default='Voltage')
@click.option('--field4', envvar='FIELD4', default='Voltage')
@click.option('--field5', envvar='FIELD5', default='Voltage')
def main(port, api_key, influxdb_url, influxdb_org, influxdb_database, influxdb_token,
         field1, field2, field3, field4, field5):
    influxdb_client = InfluxDBClient(url=influxdb_host, org=influxdb_org,
                                     token=influxdb_token, debug=False)
  
    log.info(f'Influx URL: {influxdb_url')
    log.info(f'Influx Org: {influxdb_org}')

    # Command line parameters override
    fields = {'field1': field1, 'field2': field2, 'field3': field3,
              'field4': field4, 'field5': field5}

    app = create_app(influxdb_client, influxdb_database, api_key, fields)
    log.info(f'Starting senseflux on port {port}')
    serve(app, listen=f'*:{port}')


if __name__ == '__main__':
    main()
