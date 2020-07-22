import click
from flask import Flask, request, jsonify
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


def create_app(influx_client: InfluxDBClient, test_config=None):
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
        lines = []
        readings = fields_to_values(data['updates'])
        # log.debug(f'Converted Readings {readings}')
        for r in readings:
            fields = ','.join([f'{k}="{v}"' for k, v in r.items() if k != 'created_at'])
            timestamp = int(veghub_time_to_timestamp(r['created_at']) * 1e9)
            msg = f'{channel} {fields} {timestamp}'
            log.debug(f'Line:{msg}')
            lines.append(msg)
        log.info('Sending Data to Influx')
        result = influx_client.write(lines, {'db': 'veghub'}, 204, 'line')
        log.info(f'Influx Result: {result}')
        return "Success"

    return app


@click.command()
@click.option('--port', envvar='SF_PORT', default=8003, help='Web Service Port')
@click.option('--api-key', envvar='SF_API_KEY', default=None)
@click.option('--influx-host', envvar='INFLUX_HOST', default='localhost', help='Influx Server hostname')
@click.option('--influx-port', envvar='INFLUX_PORT', default=8086, help='Influx Server port')
@click.option('--influx-database', envvar='INFLUX_DATABASE', default='senseflux')
@click.option('--influx-username', envvar='INFLUX_USERNAME', default=None)
@click.option('--influx-password', envvar='INFLUX_PASSWORD', default=None)
def main(port, api_key, influx_host, influx_port, influx_database, influx_username, influx_password):
    if influx_username and influx_password:
        influx_client = InfluxDBClient(host=influx_host, port=influx_port,
                                       username=influx_username, password=influx_password)
    else:
        influx_client = InfluxDBClient(host=influx_host, port=influx_port)
    influx_client.create_database(influx_database)
    influx_client.switch_database(influx_database)
    app = create_app(influx_client)
    serve(app, listen=f'*:{port}')
    # app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
