from .context import gfhttpva


def get_query():
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
                "ch": "ET_SASAKI:GFHTTPVA:TEST:get"
             }
           }


def test_query_timeserie(client):
    query = get_query()
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


def test_query_timeserie_error(client):
    query = get_query()
    query["targets"] = [
                        {"target": "error", "refId": "A",
                         "type": "timeserie"},
                       ]
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'RPC returned value is invalid'}
    assert json_data == res
    assert rv.status_code == 400


def test_query_table(client):
    query = get_query()
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


def test_query_table_error(client):
    query = get_query()
    query["targets"] = [
                        {"target": "error", "refId": "A",
                         "type": "table"},
                       ]
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'RPC returned labels is invalid'}
    assert json_data == res


def test_query_invalid_time(client):
    query = get_query()
    query["range"]["from"] = "2018-13-01T00:00:00:.000Z"
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'Invalid query time'}
    assert json_data == res


def test_query_invalid_query_target(client):
    query = get_query()
    del query["targets"]
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'Invalid query'}
    assert json_data == res


def test_query_invalid_query_type(client):
    query = get_query()
    del query["targets"][0]["type"]
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'Invalid query'}
    assert json_data == res


def test_query_no_target(client):
    query = get_query()
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


def test_query_empyt_ch(client):
    query = get_query()
    query["jsonData"]["ch"] = ""
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'RPC ch name is invalid'}
    assert json_data == res


def test_query_not_exist_ch(client):
    query = get_query()
    query["jsonData"]["ch"] = "NOT:EXIST:CH"
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'connection timeout'}
    assert json_data == res


def test_query_not_exist_ch_table(client):
    query = get_query()
    query["jsonData"]["ch"] = "NOT:EXIST:CH"
    query["targets"] = [{"target": "table", "refId": "B", "type": "table"}]
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'connection timeout'}
    assert json_data == res


def test_query_coincident_field(client):
    query = get_query()
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


def test_query_error_field(client):
    query = get_query()
    query["jsonData"]["ch"] = "ET_SASAKI:GFHTTPVA:TEST:get_inconsistent_field"
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'RPC returned value is invalid'}
    assert json_data == res


def test_query_error_value(client):
    query = get_query()
    query["jsonData"]["ch"] = "ET_SASAKI:GFHTTPVA:TEST:get_illegal_field"
    rv = client.post("/query", json=query)
    json_data = rv.get_json()
    res = {'message': 'RPC returned value is invalid'}
    assert json_data == res
