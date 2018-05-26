from .context import gfhttpva
from .context import config
from .context import pvaapi


class PvaRpcTimeoutConfig(config.DefaultConfig):
    PVA_RPC_TIMEOUT = 3


def test_set_timeout():
    app = gfhttpva.create_app(PvaRpcTimeoutConfig)
    assert pvaapi.TIMEOUT == 3
