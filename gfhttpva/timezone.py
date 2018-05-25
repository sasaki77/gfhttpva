import pytz


class timezone(object):
    def __init__(self):
        self.tz = None

    def set_tz(self, timezone_name):
        if timezone_name not in pytz.common_timezones:
            return False

        self.tz = pytz.timezone(timezone_name)
        return True

    def get_tz(self):
        return self.tz
