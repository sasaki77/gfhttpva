from .context import gfhttpva


def test_search(client):
    query = {"ch": "ET_SASAKI:GFHTTPVA:TEST:search",
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


def test_search_error(client):
    query = {"ch": "ET_SASAKI:GFHTTPVA:TEST:search",
             "target": "", "name": "error"}

    rv = client.post("/search", json=query)
    json_data = rv.get_json()
    res = {'message': 'RPC returned value is invalid'}
    assert json_data == res


def test_search_invalid_query(client):
    query = {"ch": "ET_SASAKI:GFHTTPVA:TEST:search"}
    rv = client.post("/search", json=query)
    json_data = rv.get_json()
    res = {'message': 'Search request invalid'}
    assert json_data == res


def test_search_invalid_query(client):
    query = {"ch": "",
             "target": "", "name": "entity"}
    rv = client.post("/search", json=query)
    json_data = rv.get_json()
    res = {'message': 'RPC ch name is invalid'}
    assert json_data == res
