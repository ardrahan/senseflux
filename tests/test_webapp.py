import unittest
from senseflux.webapp import create_app


class MockInflux(object):

    def __init__(self):
        self.data = []

    def write(self, data, params=None, expected_response_code=204,
              protocol='json'):
        self.data = data


class BasicTests(unittest.TestCase):

    test_json = """{"write_api_key":"TESTKey",
        "channel_id":"TestChn", "updates":[{"created_at":"2020-07-12 15:00:37","field1":1.827,"field2":1.541,
        "field3":0.077,"field4":1.905},{"created_at":"2020-07-12 15:05:37","field1":1.826,"field2":1.542,
        "field3":0.080,"field4":1.824},{"created_at":"2020-07-12 15:10:37","field1":1.826,"field2":1.542,
        "field3":0.081,"field4":1.907},{"created_at":"2020-07-12 15:15:37","field1":1.827,"field2":1.544}]}"""

    wrong_schema = """{"write_api_key":"TESTKey",
        "channel_id":"TestChn", "updates":[{"created_oot":"2020-07-12 15:00:37","field1":1.827,"field2":1.541,
        "field3":0.077,"field4":1.905}]}"""

    def setUp(self):
        self.influx_mock = MockInflux()
        app = create_app(self.influx_mock, 'textflux', 'TESTKey')
        self.app = app.test_client()

    def test_index(self):
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_data().decode('UTF-8'), "SenseFlux")

    def test_404(self):
        resp = self.app.get('/xxx')
        self.assertEqual(resp.status_code, 404)

    def test_veghub_valid_data(self):
        resp = self.app.post('/create/vghub', headers={'content-type': 'application/json'}, data=self.test_json)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_data().decode('UTF-8'), 'Success')
        self.assertEqual(len(self.influx_mock.data), 4)
        self.assertListEqual(self.influx_mock.data,
                             ['TestChn Humidity=60,SoilTemperature=24.21347,SoilMoisture=2,Darkness=63 1594566037000000000',
                              'TestChn Humidity=60,SoilTemperature=24.255139999999997,SoilMoisture=2,Darkness=60 1594566337000000000',
                              'TestChn Humidity=60,SoilTemperature=24.255139999999997,SoilMoisture=2,Darkness=63 1594566637000000000',
                              'TestChn Humidity=60,SoilTemperature=24.338480000000004 1594566937000000000'])

    def test_veghub_invalid_data(self):
        resp = self.app.post('/create/vghub', headers={'content-type': 'application/json'},
                             data={"write_api_key": "TESTKey, broken}}{{json"})
        self.assertEqual(resp.status_code, 400)

    def test_veghub_invalid_schema(self):
        resp = self.app.post('/create/vghub', headers={'content-type': 'application/json'},
                             data=self.wrong_schema)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.get_data().decode('UTF-8'), "Invalid VegeHub JSON: 'created_at' is a required property")
