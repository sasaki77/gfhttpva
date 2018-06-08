from datetime import datetime

import pytz

from flask import Blueprint, current_app, request, jsonify, json
from flask_cors import cross_origin

from pvaapi import valget, valget_table, get_annotation, get_search
from exception import InvalidRequest
from timezone import timezone


gfhttpva = Blueprint("gfhttpva", __name__)
methods = ("GET", "POST")
TIMEZONE = timezone()


def iso_to_dt(iso_str):
    try:
        dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S")
        tz = TIMEZONE.get_tz()
        dt = pytz.utc.localize(dt).astimezone(tz)
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise InvalidRequest("Invalid query time", status_code=400)
    except pytz.exceptions.AmbiguousTimeError:
        current_app.logger.error('pytz.exceptions.AmbiguousTimeError: %s' % dt)
        raise InvalidRequest("Invalid query time", status_code=400)
    except pytz.exceptions.InvalidTimeError:
        current_app.logger.error('pytz.exceptions.InvalidTimeError: %s' % dt)
        raise InvalidRequest("Invalid query time", status_code=400)
    except pytz.exceptions.NonExistentTimeError:
        current_app.logger.error('pytz.exceptions.NonExistentTimeError: %s'
                                 % dt)
        raise InvalidRequest("Invalid query time", status_code=400)
    except pytz.exceptions.UnknownTimeZoneError:
        current_app.logger.error('pytz.exceptions.UnknownTimeZoneError: %s'
                                 % dt)
        raise InvalidRequest("Invalid query time", status_code=400)


@gfhttpva.route("/", methods=methods)
@cross_origin()
def hello_world():
    current_app.logger.info(request.headers)
    current_app.logger.info(request.get_json())

    return "pvaccess python Grafana datasource"


@gfhttpva.route("/search", methods=methods)
@cross_origin()
def find_metrics():
    current_app.logger.info(request.headers)
    current_app.logger.info(request.get_json())

    req = request.get_json()

    try:
        ch_name = req["ch"]
        entity = req["target"]
        name = req["name"] if "name" in req else "entity"
    except KeyError:
        raise InvalidRequest("Search request invalid", status_code=400)

    res = get_search(ch_name, entity, name)

    return jsonify(res)


@gfhttpva.route("/query", methods=methods)
@cross_origin(max_age=600)
def query_metrics():
    current_app.logger.info(request.headers)
    current_app.logger.info(request.get_json())

    req = request.get_json()

    try:
        ch_name = req["jsonData"]["ch"]
        starttime = iso_to_dt(req["range"]["from"].split(".")[0])
        endtime = iso_to_dt(req["range"]["to"].split(".")[0])
        targets = req["targets"]
        labels = {"entity": req["jsonData"]["entity_label"],
                  "start": req["jsonData"]["start_label"],
                  "end": req["jsonData"]["end_label"]}
        nturi = req["jsonData"]["nturi_style"]
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
            table = valget_table(ch_name, entity, params, starttime,
                                 endtime, labels, nturi)
            return jsonify(table)

        datapoints = valget(ch_name, entity, params, starttime,
                            endtime, labels, nturi)
        res_frame = {"target": entity, "datapoints": datapoints}
        res.append(res_frame)

    return jsonify(res)


@gfhttpva.route("/annotations", methods=methods)
@cross_origin(max_age=600)
def query_annotations():
    current_app.logger.info(request.headers)
    current_app.logger.info(request.get_json())

    req = request.get_json()

    try:
        ann = req["annotation"]
        ch_name = ann["ch"]
        entity = ann["entity"]
        starttime = iso_to_dt(req["range"]["from"].split(".")[0])
        endtime = iso_to_dt(req["range"]["to"].split(".")[0])
        params = ann["params"] if "params" in req["annotation"] else {}
        labels = {"entity": req["jsonData"]["entity_label"],
                  "start": req["jsonData"]["start_label"],
                  "end": req["jsonData"]["end_label"]}
        nturi = req["jsonData"]["nturi_style"]
    except (KeyError, IndexError) as e:
        raise InvalidRequest("Invalid query", status_code=400)

    res = get_annotation(ch_name, ann, entity, params, starttime,
                         endtime, labels, nturi)
    return jsonify(res)


@gfhttpva.errorhandler(InvalidRequest)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
