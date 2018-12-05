import pytest

from .context import gfhttpva


@pytest.fixture
def query():
    return {
             "panelId": 1,
             "range": {
               "from": "2018-01-01T00:00:00.000Z",
               "to": "2018-01-01T06:00:00.000Z",
               "raw": {
                 "from": "now-6h",
                 "to": "now"
               }
             },
             "interval": "1m",
             "intervalMs": 60000,
             "targets": [{"target": "long", "refId": "A",
                          "type": "timeserie", "params": {"param1": 0}},
                         ],
             '"type": "timeserie", "params": {"param1": 0}},'
             "maxDataPoints": 399,
             "jsonData": {
                "ch": "ET_SASAKI:GFHTTPVA:TEST:get",
                "entity_label": "entity",
                "start_label": "starttime",
                "end_label": "endtime",
                "nturi_style": False
             }
           }


def test_query_timeserie(client, query):
    query["targets"] = [
                        {"target": "long", "refId": "A",
                         "type": "timeserie"},
                        {"target": "float", "refId": "B",
                         "type": "timeserie", "params": {"param1": "1"}},
                        {"target": "string", "refId": "C",
                         "type": "timeserie", "params": {"param1": "2"}}
                       ]
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = [
            {
              "target": "long",
              "datapoints": [
                [0, 1514764800000],
                [1, 1514775600000],
                [2, 1514786400000]
              ],
            },
            {
              "target": "float",
              "datapoints": [
                [1.0, 1514764800000],
                [2.0, 1514775600000],
                [3.0, 1514786400000]
              ],
            },
            {
              "target": "string",
              "datapoints": [
                ["2", 1514764800000],
                ["3", 1514775600000],
                ["4", 1514786400000]
              ],
            }
          ]
    assert json_data == res


def test_query_timeserie_error(client, query):
    query["targets"] = [
                        {"target": "error", "refId": "A",
                         "type": "timeserie"},
                       ]
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'RPC return has no requested key'}
    res["details"] = {'RPC return': "{'value': 1000}",
                      'request key': 'value'}
    assert json_data == res
    assert rv.status_code == 400


def test_query_table(client, query):
    query["targets"] = [
                        {"target": "long", "refId": "A",
                         "type": "timeserie"},
                        {"target": "table", "refId": "B",
                         "type": "table"},
                       ]
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = [
            {
              "columns": [
                {"text": "value"},
                {"text": "secondsPastEpoch"},
                {"text": "nanoseconds"},
                {"text": "status"},
                {"text": "severity"},
                {"text": "time", "type": "time"}
              ],
              "rows": [
                [1.1, 1460589140, 16235768, 0, 0, "2016-04-04T08:10:14"],
                [1.2, 1460589141, 164235245, 0, 0, "2016-04-04T08:10:15"],
                [2.0, 1460589142, 164235256, 1, 3, "2016-04-04T08:10:16"]
              ],
              "type": "table"
            }
          ]
    assert json_data == res


def test_query_table_error(client, query):
    query["targets"] = [
                        {"target": "error", "refId": "A",
                         "type": "table"},
                       ]
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'RPC returned value has no labels'}
    res["details"] = {'RPC return': "{'value': 1000}"}
    assert json_data == res


def test_query_invalid_time(client, query):
    query["range"]["from"] = "2018-13-01T00:00:00:.000Z"
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'Invalid query time'}
    res["details"] = {}
    assert json_data == res


def test_query_invalid_query_target(client, query):
    del query["targets"]
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'Invalid query'}
    res["details"] = {"request": query}
    assert json_data == res


def test_query_invalid_query_type(client, query):
    del query["targets"][0]["type"]
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'Invalid query'}
    res["details"] = {"request": query}
    assert json_data == res


def test_query_no_target(client, query):
    del query["targets"][0]["target"]
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = [
            {
              "target": "",
              "datapoints": [
                [0, 1514764800000],
                [1, 1514775600000],
                [2, 1514786400000]
              ],
            }
          ]
    assert json_data == res


def test_query_empyt_ch(client, query):
    query["jsonData"]["ch"] = ""
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'RPC ch name is empty'}
    res["details"] = {}
    assert json_data == res


def test_query_not_exist_ch(client, query):
    query["jsonData"]["ch"] = "NOT:EXIST:CH"
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'connection timeout'}
    request = ("structure \n    "
               "string endtime 2018-01-01T15:00:00\n    "
               "string param1 0\n    "
               "string starttime 2018-01-01T09:00:00\n    "
               "string entity long\n")
    res["details"] = {'ch': 'NOT:EXIST:CH', 'request': request}
    assert json_data == res


def test_query_not_exist_ch_table(client, query):
    query["jsonData"]["ch"] = "NOT:EXIST:CH"
    query["targets"] = [{"target": "table", "refId": "B", "type": "table"}]
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'connection timeout'}
    request = ("structure \n    string endtime 2018-01-01T15:00:00\n    "
               "string starttime 2018-01-01T09:00:00\n    "
               "string entity table\n")
    res["details"] = {'ch': 'NOT:EXIST:CH', 'request': request}
    assert json_data == res


def test_query_coincident_field(client, query):
    query["jsonData"]["ch"] = "ET_SASAKI:GFHTTPVA:TEST:get_consistent_field"
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = [
            {
              "target": "long",
              "datapoints": [
                [0, 0],
              ],
            }
          ]
    assert json_data == res


def test_query_error_field(client, query):
    query["jsonData"]["ch"] = "ET_SASAKI:GFHTTPVA:TEST:get_inconsistent_field"
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'RPC return has no requested key'}
    rpc_val = ("{'labels': ['value', 'secondsPastEpoch', 'nanoseconds'], "
               "'value': {'error1': array([0], dtype=uint64), "
               "'error2': array([0], dtype=uint64), "
               "'error3': array([0], dtype=uint64)}}")
    res["details"] = {'RPC return': rpc_val, 'request key': 'value'}
    assert json_data == res


def test_query_error_value(client, query):
    query["jsonData"]["ch"] = "ET_SASAKI:GFHTTPVA:TEST:get_illegal_field"
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'RPC return has no requested key'}
    rpc_val = ("{'labels': ['value', 'seconds', 'nanoseconds'], "
               "'value': {'seconds': array([0], dtype=uint64), "
               "'nanoseconds': array([0], dtype=uint64), "
               "'value': array([0], dtype=uint64)}}")
    res["details"] = {'RPC return': rpc_val, 'request key': 'secondsPastEpoch'}
    assert json_data == res


def test_query_nturi_style(client, query):
    query["jsonData"]["nturi_style"] = True
    query["jsonData"]["ch"] = "ET_SASAKI:GFHTTPVA:TEST:get_nturi_style"
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = [
            {
              "target": "long",
              "datapoints": [
                [0, 1514764800000],
                [1, 1514775600000],
                [2, 1514786400000]
              ],
            },
          ]
    assert json_data == res
