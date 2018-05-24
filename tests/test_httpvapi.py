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
                "prefix": "ET_SASAKI:GFHTTPVA:TEST:"
             }
           }


def get_annotation_query():
    return {
             "range": {
               "from": "2018-01-01T00:00:00.000Z",
               "to": "2018-01-01T06:00:00.000Z",
             },
             "rangeRaw": {
               "from": "now-24h",
               "to": "now",
             },
             u"annotation": {
               u"name": u"foo",
               u"datasource": u"bar datasource",
               u"iconColor": u"rgba(255, 96, 96, 1)",
               u"enable": True,
               u"prefix": u"ET_SASAKI:GFHTTPVA:TEST:",
               u"entity": u"foobar"
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
                {"text": "seconds"},
                {"text": "nanoseconds"},
                {"text": "status"},
                {"text": "severity"}
              ],
              "rows": [
                [1.1, 1460589140, 16235768, 0, 0],
                [1.2, 1460589141, 164235245, 0, 0],
                [2.0, 1460589142, 164235256, 1, 3]
              ],
              "type": "table"
            }
          ]
    assert json_data == res


def test_annottaion(client):
    query = get_annotation_query()
    rv = client.post("/annotations", json=query)
    json_data = rv.get_json()
    res = [
      {
        u"annotation": str(query["annotation"]),
        u"time": 1514775600000,
        u"title": query["annotation"]["entity"],
        u"tags": [u"test1", u"test2"],
        u"text": u"test text"
      },
      {
        u"annotation": str(query["annotation"]),
        u"time": 1514786400000,
        u"title": query["annotation"]["entity"]+"2",
        u"tags": [u"test1"],
        u"text": u"test text2"
      }
    ]
    assert json_data == res


def test_search(client):
    query = {"prefix": "ET_SASAKI:GFHTTPVA:TEST:",
             "target": "", "name": "entity"}

    rv = client.post("/search", json=query)
    json_data = rv.get_json()
    res = ["long", "float", "string", "str"]
    assert json_data == res

    query["target"] = "st"
    rv = client.post("/search", json=query)
    json_data = rv.get_json()
    res = ["string", "str"]
    assert json_data == res

    query["name"] = "param1"
    rv = client.post("/search", json=query)
    json_data = rv.get_json()
    res = []
    assert json_data == res
