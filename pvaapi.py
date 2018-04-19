from collections import OrderedDict
import numpy
from numpy import ndarray

import pvaccess as pva

# [TODO] effective array treatment with numpy

def create_request(entity, params, starttime, endtime):
    po_type = {"entity": pva.STRING, "starttime": pva.STRING,
               "endtime": pva.STRING}
    po_val = {"entity": str(entity), "starttime": str(starttime),
              "endtime": str(endtime)}

    for i,param in enumerate(params):
        po_type["param" + str(i+1)] = pva.STRING
        po_val["param" + str(i+1)] = str(param)

    request = pva.PvObject(po_type)
    request.set(po_val)

    return request


def create_search_request(entity, name):
    po_type = {"entity": pva.STRING, "name": pva.STRING}
    po_val = {"entity": str(entity), "name": str(name)}

    request = pva.PvObject(po_type)
    request.set(po_val)

    return request


def get_value_from_table(table, key):
    index = "column" + str(table["labels"].index(key))
    return table["value"][index]


def valget(prefix,entity, params, starttime, endtime):
    rpc = pva.RpcClient(str(prefix) + "get")

    request = create_request(entity, params, starttime, endtime)
    response = rpc.invoke(request)
    res = response.get()

    value = get_value_from_table(res, "value")
    seconds = get_value_from_table(res, "seconds")
    nano = get_value_from_table(res, "nanoseconds")

    time_ms = [sec*1000 + nano//(10**6) 
               for sec, nano in zip(seconds, nano)]

    if isinstance(value, ndarray):
        val_list = value.tolist()
    elif isinstance(value, list):
        val_list = value
    else:
        val_list = list(value)

    return zip(val_list, time_ms)


def valget_table(prefix, entity, params, starttime, endtime):
    rpc = pva.RpcClient(str(prefix) + "get")

    request = create_request(entity, params, starttime, endtime)
    response = rpc.invoke(request)
    res = response.get()

    # [TODO] validation
    columns = []
    for label in res["labels"]:
        if label.lower() == "time":
            columns.append({"text": label, "type": "time"})
        else:
            columns.append({"text": label})

    rows = []
    for i in range(len(res["value"]["column0"])):
        row = []
        for j, column in enumerate(columns):
            val = res["value"]["column"+str(j)][i]
            if isinstance(val, unicode):
                val = str(val)
            elif type(val).__module__ == numpy.__name__:
                val = float(val)
            row.append(val)
        rows.append(row)

    table = [{"columns": columns, "rows": rows, "type":"table"}]

    return table


def get_annotation(prefix, annotation, entity, params, starttime, endtime):
    rpc = pva.RpcClient(str(prefix) + "annotation")

    request = create_request(entity, params, starttime, endtime)
    response = rpc.invoke(request)
    res = response.get()

    time = get_value_from_table(res, "time")
    title = get_value_from_table(res, "title")
    tags = get_value_from_table(res, "tags")
    text = get_value_from_table(res, "text")

    annotations = []
    for tm,ti,tag,tex in zip(time, title, tags, text):
        ann = {
                "annotation": str(annotation),
                "time": int(tm),
                "title": str(ti),
                "tags": str(tag).split(),
                "text": str(tex)
              }
        annotations.append(ann)

    return annotations


def get_search(prefix, entity, name):
    rpc = pva.RpcClient(str(prefix) + "search")

    request = create_search_request(entity, name)
    response = rpc.invoke(request)
    res = response.get()

    return res["value"]
