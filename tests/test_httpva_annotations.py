from .context import gfhttpva


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
               u"ch": u"ET_SASAKI:GFHTTPVA:TEST:annotation",
               u"entity": u"foobar"
             }
           }


def test_annottaion(client):
    query = get_annotation_query()
    rv = client.post("/annotations", json=query)
    json_data = rv.get_json()
    res = [
      {
        u"annotation": query["annotation"],
        u"time": 1514775600000,
        u"title": query["annotation"]["entity"],
        u"tags": [u"test1", u"test2"],
        u"text": u"test text"
      },
      {
        u"annotation": query["annotation"],
        u"time": 1514786400000,
        u"title": query["annotation"]["entity"]+"2",
        u"tags": [u"test1"],
        u"text": u"test text2"
      }
    ]

    for data in json_data:
        data["annotation"] = eval(data["annotation"])

    assert json_data == res


def test_annottaion_error(client):
    query = get_annotation_query()
    query["annotation"]["entity"] = "error"
    rv = client.post("/annotations", json=query)
    json_data = rv.get_json()
    res = {'message': 'RPC returned value is invalid'}
    assert json_data == res


def test_annotation_invalid_query(client):
    query = get_annotation_query()
    del query["annotation"]
    rv = client.post("/annotations", json=query)
    json_data = rv.get_json()
    res = {'message': 'Invalid query'}
    assert json_data == res


def test_annotation_empty_ch(client):
    query = get_annotation_query()
    query["annotation"]["ch"] = ""
    rv = client.post("/annotations", json=query)
    json_data = rv.get_json()
    res = {'message': 'RPC ch name is invalid'}
    assert json_data == res
