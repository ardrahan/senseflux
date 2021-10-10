from typing import Dict

import jsonschema
from flask import Flask, request, Response
from influxdb_client import WritePrecision, InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from senseflux.sensors import fields_to_values
from senseflux.util import veghub_time_to_timestamp
from jsonschema import validate
import pkg_resources
import json


def load_schema():
    resource_package = __name__
    resource_path = '/'.join(('schema', 'vegehub_schema.json'))  # Do not use os.path.join()
    return json.loads(pkg_resources.resource_string(resource_package, resource_path))


def create_app(influxdb_client: InfluxDBClient, influxdb_database: str, api_key: str, field_map: Dict[str, str]):
    # create and configure the app
    from senseflux.__main__ import log
    vegehub_schema = load_schema()
    app = Flask(__name__, instance_relative_config=True)
    log.debug(f"Field Map {field_map}")

    @app.route('/')
    def default():
        log.info('SenseFlux Hello')
        return 'SenseFlux'

    @app.route('/create/vghub', methods=['POST'])
    def process_vegjson():
        log.info(f'Veghub Request {request}')

        data = request.json
        log.info(f'Data {request.data}')
        try:
            validate(instance=data, schema=vegehub_schema)
        except jsonschema.exceptions.ValidationError as err:
            log.warning(f'Invalid VegeHub JSON: {err.message}')
            return Response(f'Invalid VegeHub JSON: {err.message}', status=400)

        channel = data['channel_id'] if data['channel_id'] is not None else 'default'
        req_key = data['key']
        if api_key and api_key != req_key:
            log.warning('Invalid API Key')
            return Response(status=401)

        lines = []
        log.info(f"Raw updates {data['updates']}")
        readings = fields_to_values(data['updates'], field_map)
        for r in readings:
            fields = ','.join([f'{k}={v}' for k, v in r.items() if k != 'created_at'])
            timestamp = int(veghub_time_to_timestamp(r['created_at']) * 1e9)
            msg = f'{channel} {fields} {timestamp}'
            log.debug(f'Line:{msg}')
            lines.append(msg)
        log.info('Sending Data to Influx')
        write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
        result = write_api.write(bucket=influxdb_database, record=lines)
        log.info(f'Influx Result: {result}')
        return "Success"

    return app
