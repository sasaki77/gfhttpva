import os

from .context import gfhttpva


def test_config():
    """Test create_app without passing test config."""
    assert not gfhttpva.create_app().testing
    assert gfhttpva.create_app("gfhttpva.config.TestingConfig").testing


def test_hello(client):
    response = client.get('/')
    assert response.data == b'pvaccess python Grafana datasource'


def test_config_from_file():
    base_path = os.path.abspath((os.path.dirname(__file__)))
    config_path = os.path.join(base_path, "config.cfg")
    os.environ["GFHTTPVA_CONFIG"] = config_path
    app = gfhttpva.create_app()
    assert app.config["LOG_MAXBYTE"] == 1
    assert app.config["LOG_COUNT"] == 2
