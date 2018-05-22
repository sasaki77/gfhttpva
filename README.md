# gfhttpva - grafana http / pvAccess API gateway

This package is API gateway for [generalpvaccess-datasource](https://github.com/sasaki77/generalpvaccess-datasource).

It receives http requests from generalpvaccess-datasource and retrieves data from pvAccess RPC server.

## Installing

Before install this package you need to install [PvaPy](https://github.com/epics-base/pvaPy).

After install PvaPy, clone this package and install other requirements.

```bash
# clone the repository
git clone https://github.com/sasaki77/gfhttpva
cd gfhttpva
# install gfhttpva
pip install -e .
```

## Usage

Simple usage is below.
```bash
$ export FLASK_APP=gfhttpva
$ export FLASK_DEBUG=1
$ flask run --port=3003
```

See [here](http://flask.pocoo.org/) for more flask information.

## pvAccess RPC Server Implementation

pvAccess Server should implement 3 URIs:

- `$(prefix):get` should return metrics or table based on input
- `$(prefix):annotation` should return annotations
- `$(prefix):search` used by the find metric options on the query tab in Grafana panels (optional)

`$(prefix)` is passed from generalpvaccess-datasource.

### Example pvAccess server implementations

- https://github.com/sasaki77/grafana-pvarpc-sample
- https://github.com/sasaki77/cssalmrpc

### Get API

Example request

`starttime`, `endtime` and `entity` are necessary arguments. Any other arguments are optional which are determined by generalpvaccess-datasource settings.
```
structure 
    string starttime 2018-05-16T07:08:44
    string endtime 2018-05-16T13:08:44
    string entity point3
    string begin 5
```

Example `timeserie` reponse

`timeserie` response must has `value`, `seconds` and `nanoseconds` column. Each element name of `structure value` must be `columnX`.
```
epics:nt/NTTable:1.0 
    string[] labels [value,seconds,nanoseconds]
    structure value
        double[] column0 [5, 6, 7]
        double[] column1 [1526422268, 1526433068, 1526443868] // unixtimestamp in seconds
        double[] column2 [123456, 135246, 124536]
```

Example `table` reponse

The table can be composed of any columns but each element name of `structure value` must be `columnX`.
```
epics:nt/NTTable:1.0 
    string[] labels [value,seconds,nanoseconds,status,severity]
    structure value
        double[] column0 [1.1, 1.2, 2.0]
        double[] column1 [1460589140, 1460589141, 1460589142]
        double[] column2 [164235768, 164235245, 164235256]
        double[] column3 [0, 0, 1]
        double[] column4 [0, 0, 3]
```

### Annotation API

Example request
```
structure 
    string starttime 2018-05-16T07:08:44
    string endtime 2018-05-16T13:08:44
    string entity test
```

Example response
```
epics:nt/NTTable:1.0
    string[] labels [time,title,tags,text]
    structure value
        ulong[] column0 [1526439600000] // unixtimestamp in milliseconds
        string[] column1 [Title]
        string[] column2 [tag1 tag2]
        string[] column3 [Text]
```

### Search API

Example request
```
structure 
    string name entity
    string entity s
```

Example response
```
epics:nt/NTScalarArray:1.0 
    string[] value [sine,string]
```
