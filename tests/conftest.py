import pytest

from .context import gfhttpva


@pytest.fixture
def app():
    app = gfhttpva.create_app("gfhttpva.config.TestingConfig")
    return app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
