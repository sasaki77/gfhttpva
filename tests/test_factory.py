from .context import gfhttpva


def test_config():
    """Test create_app without passing test config."""
    assert not gfhttpva.create_app().testing
    assert gfhttpva.create_app("gfhttpva.config.TestingConfig").testing


def test_hello(client):
    response = client.get('/')
    assert response.data == b'pvaccess python Grafana datasource'
