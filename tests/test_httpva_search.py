import pytest
from .context import gfhttpva


@pytest.fixture
def query():
    query = {"ch": "ET_SASAKI:GFHTTPVA:TEST:search",
             "target": "", "name": "entity", "nturi_style": False}
    return query


def test_search(client, query):
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


def test_search_error(client, query):
    query["name"] = "error"

    rv = client.post("/search", json=query)
    json_data = rv.get_json()
    res = {'message': 'RPC returned value is invalid'}
    res["details"] = {'RPC return': 'structure \n    int value 1000\n'}
    assert json_data == res


def test_search_invalid_query(client, query):
    del query["target"]
    del query["name"]
    del query["nturi_style"]
    rv = client.post("/search", json=query)
    json_data = rv.get_json()
    res = {'message': 'Search request invalid'}
    res["details"] = {"request": query}
    assert json_data == res


def test_search_empty_ch(client, query):
    query["ch"] = ""
    rv = client.post("/search", json=query)
    json_data = rv.get_json()
    res = {'message': 'RPC ch name is empty'}
    res["details"] = {}
    assert json_data == res


def test_search_not_exist_ch(client, query):
    query["ch"] = "NOT:EXIST:CH"
    rv = client.post("/search", json=query)
    json_data = rv.get_json()
    res = {'message': 'connection timeout'}
    request = 'structure \n    string name entity\n    string entity \n'
    res["details"] = {'ch': 'NOT:EXIST:CH', 'request': request}
    assert json_data == res


def test_search_nturi_style(client, query):
    query["ch"] = "ET_SASAKI:GFHTTPVA:TEST:search_nturi_style"
    query["nturi_style"] = True
    rv = client.post("/search", json=query)
    json_data = rv.get_json()
    res = ["long", "float", "string", "str"]
    assert json_data == res
