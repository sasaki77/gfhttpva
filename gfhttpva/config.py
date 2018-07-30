class DefaultConfig(object):
    """
    Class for default configuration
    """

    LOG_PATH = None
    LOG_MAXBYTE = 80000
    LOG_COUNT = 1
    TIMEZONE = "Asia/Tokyo"
    PVA_RPC_TIMEOUT = 5


class TestingConfig(DefaultConfig):
    """
    Class for test configuration
    """

    TESTING = True
    PVA_RPC_TIMEOUT = 1
