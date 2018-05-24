import math
import time
import argparse
from datetime import datetime

from collections import OrderedDict

import pytz

import pvaccess as pva


ENTITIES = ["long", "float", "string", "str"]
TYPES = {"long": pva.LONG, "float": pva.FLOAT, "string": pva.STRING}

class PvaServer():

    def __init__(self, prefix=""):
        self.srv = pva.RpcServer()
        self.srv.registerService(prefix + "get", self.get)
        self.srv.registerService(prefix + "search", self.search)
        self.srv.registerService(prefix + "annotation", self.annotation)

    def run(self):
        self.srv.startListener()

    def stop(self):
        self.srv.stopListener()

    def get(self, x):
        try:
            entity = x.getString("entity")
            starttime = x.getString("starttime")
            endtime = x.getString("endtime")
        except (pva.FieldNotFound, pva.InvalidRequest):
            return pva.PvString("error")
    
        param1 = int(x.getString("param1")) if x.hasField("param1") else 0
    
        str_sec = self.is_to_unixtime_seconds(starttime)
        end_sec = self.is_to_unixtime_seconds(endtime)

        if entity == "table":
            table = self.get_table(entity, str_sec, end_sec, param1)
        else:
            table = self.get_timesrie(entity, str_sec, end_sec, param1)
    
        return table

    def get_timesrie(self, entity, str_sec, end_sec, param1):
        interval = (end_sec - str_sec)//2

        value = []
        seconds = []
        nano = []
        for i in range(3):
            if entity == "string" or entity == "str":
                value.append(str(param1+i))
            else:
                value.append(param1+i)
            seconds.append(str_sec + i*interval)
            nano.append(0)
        val_type = TYPES.get(entity, pva.LONG)
    
        vals = OrderedDict([("column0", [val_type]),
                            ("column1", [pva.DOUBLE]),
                            ("column2", [pva.DOUBLE])])
        table = pva.PvObject(OrderedDict({"labels": [pva.STRING], "value": vals}),
                             "epics:nt/NTTable:1.0")
        table.setScalarArray("labels", ["value", "seconds", "nanoseconds"])
        table.setStructure("value", OrderedDict({"column0": value,
                                                 "column1": seconds,
                                                 "column2": nano}))

        return table

    def get_table(self, entity, str_sec, end_sec, param1):
        interval = (end_sec - str_sec)//2

        value = [1.1, 1.2, 2.0]
        seconds = [1460589140, 1460589141, 1460589142]
        nano = [16235768, 164235245, 164235256]
        status = [0, 0, 1]
        severity = [0, 0, 3]
    
        vals = OrderedDict([("column0", [pva.DOUBLE]),
                            ("column1", [pva.DOUBLE]),
                            ("column2", [pva.DOUBLE]),
                            ("column3", [pva.ULONG]),
                            ("column4", [pva.ULONG])])
        table = pva.PvObject(OrderedDict({"labels": [pva.STRING], "value": vals}),
                             "epics:nt/NTTable:1.0")
        table.setScalarArray("labels", ["value", "seconds", "nanoseconds",
                                        "status", "severity"])
        table.setStructure("value", OrderedDict({"column0": value,
                                                 "column1": seconds,
                                                 "column2": nano,
                                                 "column3": status,
                                                 "column4": severity}))

        return table
    
    
    def search(self, x):
        try:
            query = x.getString("entity")
            name = x.getString("name")
        except (pva.FieldNotFound, pva.InvalidRequest):
            return pva.PvString("error")
    
        org_value = ENTITIES if str(name) == "entity" else []
    
        value = [val for val in org_value if val.startswith(query)]
    
        pv = pva.PvObject({"value": [pva.STRING]}, "epics:nt/NTScalarArray:1.0")
        pv["value"] = value
    
        return pv
    
    
    def annotation(self, x):
        try:
            entity = x.getString("entity")
            starttime = x.getString("starttime")
            endtime = x.getString("endtime")
        except (pva.FieldNotFound, pva.InvalidRequest):
            return pva.PvString("error")
    
        str_sec = self.is_to_unixtime_seconds(starttime)
        end_sec = self.is_to_unixtime_seconds(endtime)
    
        time = [(int(end_sec) + int(str_sec))//2*1000, end_sec*1000]
        title = [entity, entity+"2"]
        tags = ["test1 test2", "test1"]
        text = ["test text", "test text2"]
    
        vals = OrderedDict([("column0", [pva.ULONG]),
                            ("column1", [pva.STRING]),
                            ("column2", [pva.STRING]),
                            ("column3", [pva.STRING])])
        table = pva.PvObject(OrderedDict({"labels": [pva.STRING], "value": vals}),
                             "epics:nt/NTTable:1.0")
        table.setScalarArray("labels", ["time", "title", "tags", "text"])
        table.setStructure("value", OrderedDict({"column0": time,
                                                 "column1": title,
                                                 "column2": tags,
                                                 "column3": text}))
    
        return table

    def is_to_unixtime_seconds(self, iso_str):
        dt = None
        try:
            dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            print "Invalid time"
        return int(dt.strftime("%s"))