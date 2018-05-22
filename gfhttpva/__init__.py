import os

from flask import Flask
from flask_cors import CORS

from .gfhttpva import gfhttpva


def create_app(config):
    app = Flask(__name__)
    app.register_blueprint(gfhttpva)

    cors = CORS(app)
    app.config["CORS_HEADERS"] = "Content-Type"

    return app
