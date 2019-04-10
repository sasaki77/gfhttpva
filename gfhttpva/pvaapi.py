import sys
from threading import RLock

import numpy as np
import pandas as pd

import pvaccess as pva
from .exception import InvalidRequest

from flask import current_app


class Pvaapi(object):
    """
    pvAccess api wrapper

    Attributes
    ----------
    timeout : float
        timeout for pvAccess RPC in seconds
    _clients : dict
        pvAccess RpcClient for ch name
    _lock : threading.RLock
        lock for _clients
    """

    def __init__(self, timeout=1):
        self.timeout = timeout
        self._clients = {}
        self._lock = RLock()

    def _get_rpc_client(self, ch_name):
        """Get pvAccess RPC Client

        Parameters
        ----------
        ch_name : str
            pvAccess channel name

        Returns
        -------
        pvaccess.RpcClient
            pvAccess RPC Client for channel name
        """
        self._check_ch_name(ch_name)
        name = str(ch_name)

        with self._lock:
            if name not in self._clients:
                self._clients[name] = pva.RpcClient(name)
            client = self._clients[name]

        return client

    def _create_request(self, entity, params, starttime, endtime,
                        labels, path="", nturi=False):
        """Create pvAccess RPC request

        Parameters
        ----------
        entity : str or unicode
            query entity
        params : dict
            parameters for optional RPC request query
        starttime : str or unicode
            start time as string
        endtime : str or unicode
            end time as string
        labels : dict
            labels for entity, starttime and endtime
        path : str
            path for nturi style path
        nturi : bool
            whether create request as nturi style or not

        Returns
        -------
        pvaccess.PvObject
            pvAccess RPC request pvData
        """

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

        request = self._create_request_pvdate(query_type, query_val,
                                              path, nturi)

        return request

    def _create_search_request(self, entity, name, path="", nturi=False):
        """Create pvAccess RPC request for find metrics

        Parameters
        ----------
        entity : str or unicode
            query entity
        name: str or unicode
            name to find metrics
        path : str
            path for nturi style path

        Returns
        -------
        pvaccess.PvObject
            pvAccess RPC request pvData for find mertics
        """

        query_type = {"entity": pva.STRING, "name": pva.STRING}
        query_val = {"entity": str(entity), "name": str(name)}

        request = self._create_request_pvdate(query_type, query_val,
                                              path, nturi)

        return request

    def _create_request_pvdate(self, query_type, query_val,
                               path="", nturi=False):
        """Create RPC request pvData

        Parameters
        ----------
        query_type : dict
            dict of pvaccess type for query
        query_val : dict
            dict of query value
        path : str
            path for nturi style path
        nturi : bool
            whether create request as nturi style or not

        Returns
        -------
        pvaccess.PvObject
            pvAccess RPC request pvData
        """

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

    def _get_value_from_table(self, table, key):
        """Get value from NTTable style dict

        Parameters
        ----------
        table : dict
            dict of NTTable style dict
        key : str
            required column name

        Returns
        -------
        list
            required column values

        Raises
        ------
        InvalidRequest
            if table has no requered key
        """

        try:
            if key in table["value"]:
                return table["value"][key]
            else:
                index = "column" + str(table["labels"].index(key))
                return table["value"][index]
        except (KeyError, ValueError, TypeError) as e:
            current_app.logger.error("get_value_from_table: KeyError")
            details = {"request key": key, "RPC return": str(table)}
            raise InvalidRequest("RPC return has no requested key",
                                 status_code=400,
                                 details=details)

    def _check_ch_name(self, ch_name):
        """Check RPC channel name is valid

        Parameters
        ----------
        ch_name : str or unicode
            channel name

        Raises
        ------
        InvalidRequest
            if channel name is invalid
        """

        if not ch_name:
            current_app.logger.error("valget: Empty ch name")
            raise InvalidRequest("RPC ch name is empty", status_code=400)

    def valget(self, ch_name, entity, params, starttime, endtime,
               labels, nturi):
        """Get timesiries values using pvAccess RPC

        Parameters
        ----------
        ch_name : str or unicode
            channel name of pvAccess RPC
        entity : str or unicode
            query entity
        params : dict
            parameters for optional RPC request query
        starttime : str or unicode
            start time as string
        endtime : str or unicode
            end time as string
        labels : dict
            labels for entity, starttime and endtime
        nturi : bool
            whether create request as nturi style or not

        Returns
        -------
        tuple
            tuble of value and its time

        Raises
        ------
        InvalidRequest
            if failed to call pvAccess RPC
        """

        rpc = self._get_rpc_client(str(ch_name))

        request = self._create_request(entity, params, starttime,
                                       endtime, labels, ch_name, nturi)
        try:
            response = rpc.invoke(request, self.timeout)
        except pva.PvaException as e:
            raise InvalidRequest(str(e), status_code=400,
                                 details={"request": str(request),
                                          "ch": ch_name}
                                 )

        res = response.get()

        value = self._get_value_from_table(res, "value")
        seconds = self._get_value_from_table(res, "secondsPastEpoch")
        nano = self._get_value_from_table(res, "nanoseconds")

        time_ms = np.trunc(seconds*1000 + nano//(10**6))

        datapoints = pd.DataFrame({"value": value, "time": time_ms})

        # order of datapoints' columns  must be value, time for tolist
        datapoints = datapoints[['value', 'time']]

        return datapoints.values.tolist()

    def valget_table(self, ch_name, entity, params,
                     starttime, endtime, labels, nturi):
        """Get table values using pvAccess RPC

        Parameters
        ----------
        ch_name : str or unicode
            channel name of pvAccess RPC
        entity : str or unicode
            query entity
        params : dict
            parameters for optional RPC request query
        starttime : str or unicode
            start time as string
        endtime : str or unicode
            end time as string
        labels : dict
            labels for entity, starttime and endtime
        nturi : bool
            whether create request as nturi style or not

        Returns
        -------
        list of dict
            list of table values dict

        Raises
        ------
        InvalidRequest
            if failed to call pvAccess RPC
        """

        rpc = self._get_rpc_client(str(ch_name))

        request = self._create_request(entity, params, starttime,
                                       endtime, labels, ch_name, nturi)
        try:
            response = rpc.invoke(request, self.timeout)
        except pva.PvaException as e:
            raise InvalidRequest(str(e), status_code=400,
                                 details={"request": str(request),
                                          "ch": ch_name}
                                 )

        res = response.get()

        try:
            labels = res["labels"]
        except KeyError:
            current_app.logger.error("valget_table: label KeyError")
            raise InvalidRequest("RPC returned value has no labels",
                                 status_code=400,
                                 details={"RPC return": str(res)})

        columns = []
        for label in labels:
            if label.lower() == "time":
                columns.append({"text": label, "type": "time"})
            else:
                columns.append({"text": label})

        try:
            frame_dict = {label: res["value"]["column"+str(i)]
                          for i, label in enumerate(labels)}
        except KeyError:
            current_app.logger.error("valget_table: value KeyError")
            raise InvalidRequest("RPC returned value key error",
                                 status_code=400,
                                 details={"RPC return": str(res)})

        frame = pd.DataFrame(frame_dict)

        # order of frame's columns must be labels' order for tolist
        frame = frame[labels]

        table = [{"columns": columns,
                  "rows": frame.values.tolist(),
                  "type": "table"}]

        return table

    def get_annotation(self, ch_name, annotation, entity, params,
                       starttime, endtime, labels, nturi):
        """Get annotation values using pvAccess RPC

        Parameters
        ----------
        ch_name : str or unicode
            channel name of pvAccess RPC
        annotation : str or unicode
            annotation to return it as is
        entity : str or unicode
            query entity
        params : dict
            parameters for optional RPC request query
        starttime : str or unicode
            start time as string
        endtime : str or unicode
            end time as string
        labels : dict
            labels for entity, starttime and endtime
        nturi : bool
            whether create request as nturi style or not

        Returns
        -------
        tuple
            tuble of value and its time

        Raises
        ------
        InvalidRequest
            if failed to call pvAccess RPC
        """

        rpc = self._get_rpc_client(str(ch_name))

        request = self._create_request(entity, params, starttime,
                                       endtime, labels, ch_name, nturi)
        try:
            response = rpc.invoke(request, self.timeout)
        except pva.PvaException as e:
            raise InvalidRequest(str(e), status_code=400,
                                 details={"request": str(request),
                                          "ch": ch_name}
                                 )

        if hasattr(response, "useNumPyArrays"):
            response.useNumPyArrays = False

        res = response.get()

        time = self._get_value_from_table(res, "time")
        title = self._get_value_from_table(res, "title")
        tags = self._get_value_from_table(res, "tags")
        text = self._get_value_from_table(res, "text")

        annotations = []
        for tm, ti, tag, tex in zip(time, title, tags, text):
            ann = {
                    "annotation": str(annotation),
                    "time": int(tm),
                    "title": str(ti),
                    "tags": str(tag).split(","),
                    "text": str(tex)
                  }
            annotations.append(ann)

        return annotations

    def get_search(self, ch_name, entity, name, nturi):
        """Get search values using pvAccess RPC

        Parameters
        ----------
        ch_name : str or unicode
            channel name of pvAccess RPC
        entity : str or unicode
            query entity
        name : str or unicoe
            name to find metrics
        nturi : bool
            whether create request as nturi style or not

        Returns
        -------
        list
            list of searched metrics

        Raises
        ------
        InvalidRequest
            if failed to call pvAccess RPC
        """

        rpc = self._get_rpc_client(str(ch_name))

        request = self._create_search_request(entity, name, ch_name, nturi)
        try:
            response = rpc.invoke(request, self.timeout)
        except pva.PvaException as e:
            raise InvalidRequest(str(e), status_code=400,
                                 details={"request": str(request),
                                          "ch": ch_name}
                                 )

        if hasattr(response, "useNumPyArrays"):
            response.useNumPyArrays = False

        try:
            res = response.getScalarArray("value")
        except (pva.FieldNotFound, pva.InvalidRequest):
            current_app.logger.error("get_search: response get error")
            raise InvalidRequest("RPC returned value is invalid",
                                 status_code=400,
                                 details={"RPC return": str(response)})

        return res


pvaapi = Pvaapi()
