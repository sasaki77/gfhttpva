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
    details : obj
        optional details to give more context for the error
    """

    status_code = 400

    def __init__(self, message, status_code=None, details=None):
        """
        Parameters
        ----------
        message : str
            The message of error response
        status_code : int, optional
            The status code of error response(default is None)
        details : obj, optional
            The optional details for error response(default is None)
        """

        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.details = details

    def to_dict(self):
        """Return message and details as dict

        Returns
        -------
        dict
            a dict which has message and optional details
        """

        rv = {'details': dict(self.details or "")}
        rv['message'] = self.message
        return rv
