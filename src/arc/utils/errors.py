class DataReportError(Exception):
    """
    Base exception for all errors in the data_report project.
    """
    pass


class APIError(DataReportError):
    """
    Exception raised when there is an error with an external API call.
    
    Attributes:
        message: Explanation of the error.
        status_code: Optional HTTP status code or error code from the API.
    """

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class DataProcessingError(DataReportError):
    """
    Exception raised during data processing tasks.
    """
    pass


class ConfigurationError(DataReportError):
    """
    Exception raised when there is a configuration issue, such as missing environment variables.
    """
    pass
