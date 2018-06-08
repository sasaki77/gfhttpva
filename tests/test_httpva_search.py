from .context import gfhttpva


def get_search_query():
    query = {"ch": "ET_SASAKI:GFHTTPVA:TEST:search",
             "target": "", "name": "entity", "nturi_style": False}
    return query


def test_search(client):
    query = get_search_query()

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
    query = get_search_query()
    query["name"] = "error"

    rv = client.post("/search", json=query)
    json_data = rv.get_json()
    res = {'message': 'RPC returned value is invalid'}
    assert json_data == res


def test_search_invalid_query(client):
    query = get_search_query()
    del query["target"]
    del query["name"]
    del query["nturi_style"]
    rv = client.post("/search", json=query)
    json_data = rv.get_json()
    res = {'message': 'Search request invalid'}
    assert json_data == res


def test_search_empty_ch(client):
    query = get_search_query()
    query["ch"] = ""
    rv = client.post("/search", json=query)
    json_data = rv.get_json()
    res = {'message': 'RPC ch name is invalid'}
    assert json_data == res


def test_search_not_exist_ch(client):
    query = get_search_query()
    query["ch"] = "NOT:EXIST:CH"
    rv = client.post("/search", json=query)
    json_data = rv.get_json()
    res = {'message': 'connection timeout'}
    assert json_data == res


def test_search_nturi_style(client):
    query = get_search_query()
    query["ch"] = "ET_SASAKI:GFHTTPVA:TEST:search_nturi_style"
    query["nturi_style"] = True
    rv = client.post("/search", json=query)
    json_data = rv.get_json()
    res = ["long", "float", "string", "str"]
    assert json_data == res
