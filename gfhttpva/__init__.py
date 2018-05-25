import os
from logging import Formatter
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask.logging import default_handler
from flask_cors import CORS

from .config import DefaultConfig
from .gfhttpva import gfhttpva, TIMEZONE


def create_app(config_obj="gfhttpva.config.DefaultConfig"):
    """
    Arguments:
    object_name: the python path of the config object,
                 e.g. gfhttpva.config.DefaultConfig
    """
    app = Flask(__name__)

    app.config.from_object(config_obj)
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

    # settings for timezone
    tz = app.config["TIMEZONE"]
    tz_success = TIMEZONE.set_tz(tz)
    if not tz_success:
        app.logger.error("Specified TIMEZONE is invalid. "
                         "Set TIMEZONE as UTC.")
        TIMEZONE.set_tz("UTC")

    app.register_blueprint(gfhttpva)

    cors = CORS(app)
    app.config["CORS_HEADERS"] = "Content-Type"

    return app
