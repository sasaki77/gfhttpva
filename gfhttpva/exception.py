from flask import jsonify


class InvalidRequest(Exception):
    """
    A class used to raise invalid request exception on Flask

    Attributes
    ----------
    message : str
        error message for error response
    status_code : int
        status code for error response
    payload : str
        optional payload to give more context for the error

    Methods
    -------
    to_dict()
        return message and payload as dict
    """

    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        """
        Parameters
        ----------
        message : str
            The message of error response
        status_code : int, optional
            The status code of error response(default is None)
        payload : obj, optional
            The optional payload for error response(default is None)
        """

        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Return message and payload as dict

        Returns
        -------
        dict
            a dict which has message and optional payload
        """

        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
