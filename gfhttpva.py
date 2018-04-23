from datetime import datetime

import pytz

from flask import Flask, request, jsonify, json, abort
from flask_cors import CORS, cross_origin

from pvaapi import valget, valget_table, get_annotation, get_search

app = Flask(__name__)

cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

methods = ("GET", "POST")


def iso_to_dt(iso_str):
    dt = None
    try:
        dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S")
        dt = pytz.utc.localize(dt).astimezone(pytz.timezone("Asia/Tokyo"))
    except:
        print "err"
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


@app.route("/", methods=methods)
@cross_origin()
def hello_world():
    print request.headers, request.get_json()
    return "pvaccess python Grafana datasource, used for rendering HTML panels and timeseries data."


@app.route("/search", methods=methods)
@cross_origin()
def find_metrics():
    print request.headers, request.get_json()
    req = request.get_json()

    try:
        prefix = req["prefix"]
        entity = req["target"]
        name = req["name"] if "name" in req else "entity"
    except KeyError:
        return

    res = get_search(prefix, entity, name)

    return jsonify([res])


@app.route("/query", methods=methods)
@cross_origin(max_age=600)
def query_metrics():
    print request.headers, request.get_json()
    req = request.get_json()

    try:
        prefix = req["jsonData"]["prefix"]
        starttime = iso_to_dt(req["range"]["from"].split(".")[0])
        endtime = iso_to_dt(req["range"]["to"].split(".")[0])
        targets = req["targets"]
    except (KeyError, IndexError) as e:
        return

    res = []
    for target in targets:
        params = target["params"] if "params" in target else {}
        entity = target["target"] if "target" in target else ""

        try:
            ttype = target["type"]
        except KeyError:
            return

        if ttype == "table":
            table = valget_table(prefix, entity,
                                 params, starttime, endtime)
            return jsonify(table)

        datapoints = valget(prefix, entity,
                            params, starttime, endtime)
        res_frame = {"target": entity, "datapoints": datapoints}
        res.append(res_frame)

    return jsonify(res)


@app.route("/annotations", methods=methods)
@cross_origin(max_age=600)
def query_annotations():
    print request.headers, request.get_json()
    req = request.get_json()

    try:
        ann = req["annotation"]
        prefix = ann["prefix"]
        entity = ann["entity"]
        starttime = iso_to_dt(req["range"]["from"].split(".")[0])
        endtime = iso_to_dt(req["range"]["to"].split(".")[0])
        params = ann["params"] if "params" in req["annotation"] else {}
    except (KeyError, IndexError) as e:
        return

    res = get_annotation(prefix, ann, entity,
                         params, starttime, endtime)
    return jsonify(res)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3004, debug=True)
