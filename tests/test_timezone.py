import pytz

from .context import gfhttpva
from .context import config
from .context import TIMEZONE


class TimezoneErrorTestConfig(config.DefaultConfig):
    TIMEZONE = "ERROR/TZ"


def test_timezone():
    app = gfhttpva.create_app(TimezoneErrorTestConfig)
    tz = TIMEZONE.get_tz()
    assert tz == pytz.utc
