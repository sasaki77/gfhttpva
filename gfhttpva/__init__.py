import os
from logging import Formatter
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask.logging import default_handler
from flask_cors import CORS

from .config import DefaultConfig
from .gfhttpva import gfhttpva


def create_app():
    app = Flask(__name__)

    app.config.from_object(DefaultConfig)
    if "GFHTTPVA_CONFIG" in os.environ:
        app.config.from_envvar('GFHTTPVA_CONFIG')

    app.logger.addHandler(default_handler)

    # settings for rotations handler
    log_path = app.config["LOG_PATH"]
    log_byte = app.config["LOG_MAXBYTE"]
    log_count = app.config["LOG_COUNT"]
    if log_path:
        rhandler = RotatingFileHandler(log_path, maxBytes=log_byte,
                                       backupCount=log_count)
        fmt = Formatter('[%(asctime)s] %(levelname)s in '
                        '%(module)s: %(message)s')
        rhandler.setFormatter(fmt)
        app.logger.addHandler(rhandler)

    app.register_blueprint(gfhttpva)

    cors = CORS(app)
    app.config["CORS_HEADERS"] = "Content-Type"

    return app
