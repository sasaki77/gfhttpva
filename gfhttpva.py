from datetime import datetime

import pytz

from flask import Flask, request, jsonify, json, abort
from flask_cors import CORS, cross_origin

from pvaapi import valget, valget_table, get_annotation, get_search
from exception import InvalidRequest

app = Flask(__name__)

cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

methods = ("GET", "POST")


def iso_to_dt(iso_str):
    try:
        dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S")
        dt = pytz.utc.localize(dt).astimezone(pytz.timezone("Asia/Tokyo"))
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except:
        raise InvalidRequest("Invalid query time", status_code=400)


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
        raise InvalidRequest("Search request invalid", status_code=400)

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
        raise InvalidRequest("Invalid query", status_code=400)

    res = []
    for target in targets:
        params = target["params"] if "params" in target else {}
        entity = target["target"] if "target" in target else ""

        try:
            ttype = target["type"]
        except KeyError:
            raise InvalidRequest("Invalid query", status_code=400)

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
        raise InvalidRequest("Invalid query", status_code=400)

    res = get_annotation(prefix, ann, entity,
                         params, starttime, endtime)
    return jsonify(res)


@app.errorhandler(InvalidRequest)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3004, debug=True)
