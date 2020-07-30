import jsonschema
from flask import Flask, request, Response
from influxdb import InfluxDBClient
from senseflux.sensors import fields_to_values
from senseflux.util import veghub_time_to_timestamp
from jsonschema import validate
import pkg_resources
import json


def load_schema():
    resource_package = __name__
    resource_path = '/'.join(('schema', 'vegehub_schema.json'))  # Do not use os.path.join()
    return json.loads(pkg_resources.resource_string(resource_package, resource_path))


def create_app(influxdb_client: InfluxDBClient, influxdb_database: str, api_key: str):
    # create and configure the app
    from senseflux.__main__ import log
    vegehub_schema = load_schema()
    app = Flask(__name__, instance_relative_config=True)

    @app.route('/')
    def default():
        log.info('SenseFlux Hello')
        return 'SenseFlux'

    @app.route('/create/vghub', methods=['POST'])
    def process_vegjson():
        log.info('Veghub Request')

        data = request.json
        try:
            validate(instance=data, schema=vegehub_schema)
        except jsonschema.exceptions.ValidationError as err:
            return Response(f'Invalid VegeHub JSON: {err.message}', status=400)

        channel = data['channel_id']
        req_key = data['write_api_key']
        if api_key and api_key != req_key:
            log.warning('Invalid API Key')
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
