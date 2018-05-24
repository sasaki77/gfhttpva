class DefaultConfig(object):
    LOG_PATH = None
    LOG_MAXBYTE = 80000
    LOG_COUNT = 1


class TestingConfig(DefaultConfig):
    TESTING = True
