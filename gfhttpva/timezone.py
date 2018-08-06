import pytz


class timezone(object):
    """
    Timezone to manage it in programs

    Attributes
    ----------
    tz : pytz.timezone
        timezone
    """

    def __init__(self):
        self.tz = None

    def set_tz(self, timezone_name):
        """Set timezone with timezone name

        Parameters
        ----------
        timezone_name : str
            name of timezone

        Returns
        -------
        bool
            Return if timezone is set correctly
        """

        if timezone_name not in pytz.common_timezones:
            return False

        self.tz = pytz.timezone(timezone_name)
        return True

    def get_tz(self):
        """Get timezone

        Returns
        -------
        pytz.timezone
            timezone in this program
        """

        return self.tz
