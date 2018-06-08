from collections import OrderedDict

import pvaccess as pva
from exception import InvalidRequest

from flask import current_app

TIMEOUT = 1


def create_request(entity, params, starttime, endtime,
                   labels, path="", nturi=False):

    l_entity = str(labels["entity"])
    l_start = str(labels["start"])
    l_end = str(labels["end"])

    query_type = {l_entity: pva.STRING,
                  l_start: pva.STRING,
                  l_end: pva.STRING}
    query_val = {l_entity: str(entity),
                 l_start: str(starttime),
                 l_end: str(endtime)}

    for key, val in params.items():
        query_type[str(key)] = pva.STRING
        query_val[str(key)] = str(val)

    request = create_request_pvdate(query_type, query_val, path, nturi)

    return request


def create_search_request(entity, name, path="", nturi=False):
    query_type = {"entity": pva.STRING, "name": pva.STRING}
    query_val = {"entity": str(entity), "name": str(name)}

    request = create_request_pvdate(query_type, query_val, path, nturi)

    return request


def create_request_pvdate(query_type, query_val, path="", nturi=False):
    if nturi:
        request = pva.PvObject({"scheme": pva.STRING,
                                "authority": pva.STRING,
                                "path": pva.STRING,
                                "query": query_type
                                },
                               "epics:nt/NTURI:1.0")
        request["scheme"] = "pva"
        request["authority"] = ""
        request["path"] = str(path)
        request.setStructure("query", query_val)
    else:
        request = pva.PvObject(query_type)
        request.set(query_val)

    return request


def get_value_from_table(table, key):
    try:
        if key in table["value"]:
            return table["value"][key]
        else:
            index = "column" + str(table["labels"].index(key))
            return table["value"][index]
    except (KeyError, ValueError, TypeError) as e:
        current_app.logger.error("get_value_from_table: KeyError")
        raise InvalidRequest("RPC returned value is invalid", status_code=400)


def check_ch_name(ch_name):
    if not ch_name:
        current_app.logger.error("valget: Empty ch name")
        raise InvalidRequest("RPC ch name is invalid", status_code=400)


def valget(ch_name, entity, params, starttime, endtime, labels, nturi):
    check_ch_name(ch_name)
    rpc = pva.RpcClient(str(ch_name))

    request = create_request(entity, params, starttime, endtime, labels,
                             ch_name, nturi)
    try:
        response = rpc.invoke(request, TIMEOUT)
    except pva.PvaException as e:
        raise InvalidRequest(e.message, status_code=400)

    if hasattr(response, "useNumPyArrays"):
        response.useNumPyArrays = False

    res = response.get()

    value = get_value_from_table(res, "value")
    seconds = get_value_from_table(res, "secondsPastEpoch")
    nano = get_value_from_table(res, "nanoseconds")

    time_ms = [sec*1000 + nano//(10**6)
               for sec, nano in zip(seconds, nano)]

    return zip(list(value), time_ms)


def valget_table(ch_name, entity, params, starttime, endtime, labels, nturi):
    check_ch_name(ch_name)
    rpc = pva.RpcClient(str(ch_name))

    request = create_request(entity, params, starttime, endtime, labels,
                             ch_name, nturi)
    try:
        response = rpc.invoke(request, TIMEOUT)
    except pva.PvaException as e:
        raise InvalidRequest(e.message, status_code=400)

    if hasattr(response, "useNumPyArrays"):
        response.useNumPyArrays = False

    res = response.get()

    try:
        labels = res["labels"]
    except KeyError:
        current_app.logger.error("valget_table: label KeyError")
        raise InvalidRequest("RPC returned labels is invalid", status_code=400)

    columns = []
    for label in labels:
        if label.lower() == "time":
            columns.append({"text": label, "type": "time"})
        else:
            columns.append({"text": label})

    try:
        rows_T = [res["value"]["column"+str(i)] for i in range(len(columns))]
        rows = [[row[i] for row in rows_T] for i in range(len(rows_T[0]))]
    except KeyError:
        current_app.logger.error("valget_table: value KeyError")
        raise InvalidRequest("RPC returned value is invalid", status_code=400)

    table = [{"columns": columns, "rows": rows, "type": "table"}]

    return table


def get_annotation(ch_name, annotation, entity, params,
                   starttime, endtime, labels, nturi):
    check_ch_name(ch_name)
    rpc = pva.RpcClient(str(ch_name))

    request = create_request(entity, params, starttime, endtime, labels,
                             ch_name, nturi)
    try:
        response = rpc.invoke(request, TIMEOUT)
    except pva.PvaException as e:
        raise InvalidRequest(e.message, status_code=400)

    if hasattr(response, "useNumPyArrays"):
        response.useNumPyArrays = False

    res = response.get()

    time = get_value_from_table(res, "time")
    title = get_value_from_table(res, "title")
    tags = get_value_from_table(res, "tags")
    text = get_value_from_table(res, "text")

    annotations = []
    for tm, ti, tag, tex in zip(time, title, tags, text):
        ann = {
                "annotation": str(annotation),
                "time": int(tm),
                "title": str(ti),
                "tags": str(tag).split(),
                "text": str(tex)
              }
        annotations.append(ann)

    return annotations


def get_search(ch_name, entity, name, nturi):
    check_ch_name(ch_name)
    rpc = pva.RpcClient(str(ch_name))

    request = create_search_request(entity, name, ch_name, nturi)
    try:
        response = rpc.invoke(request, TIMEOUT)
    except pva.PvaException as e:
        raise InvalidRequest(e.message, status_code=400)

    if hasattr(response, "useNumPyArrays"):
        response.useNumPyArrays = False

    try:
        res = response.getScalarArray("value")
    except (pva.FieldNotFound, pva.InvalidRequest):
        current_app.logger.error("get_search: response get error")
        raise InvalidRequest("RPC returned value is invalid", status_code=400)

    return res
