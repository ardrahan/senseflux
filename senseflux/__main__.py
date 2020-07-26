import click
from flask import Flask, request, jsonify, Response
from influxdb import InfluxDBClient
from waitress import serve

from senseflux.sensors import fields_to_values
from senseflux.util import veghub_time_to_timestamp
import logging

console = logging.StreamHandler()
console.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
log = logging.getLogger("senseflux")
log.addHandler(console)
log.setLevel(logging.DEBUG)


def create_app(influxdb_client: InfluxDBClient, influxdb_database: str, api_key: str, test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    # )

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)
    #
    # # ensure the instance folder exists
    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass

    # a simple page that says hello
    @app.route('/')
    def default():
        return 'SenseFlux'

    @app.route('/create/vghub', methods=['POST'])
    def process_vegjson():
        data = request.json
        channel = data['channel_id']
        req_key = data['write_api_key']
        if api_key and api_key != req_key:
            return Response(status=401)

        lines = []
        log.info(f"Raw updates {data['updates']}")
        readings = fields_to_values(data['updates'])
        for r in readings:
            fields = ','.join([f'{k}={v}' for k, v in r.items() if k != 'created_at'])
            timestamp = int(veghub_time_to_timestamp(r['created_at']) * 1e9)
            msg = f'{channel} {fields} {timestamp}'
            log.debug(f'Line:{msg}')
            lines.append(msg)
        log.info('Sending Data to Influx')
        result = influxdb_client.write(lines, {'db': influxdb_database}, 204, 'line')
        log.info(f'Influx Result: {result}')
        return "Success"

    return app


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
    app = create_app(influxdb_client, influxdb_database, api_key)
    serve(app, listen=f'*:{port}')


if __name__ == '__main__':
    main()
