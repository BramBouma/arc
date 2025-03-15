from fredapi import Fred
from config import get_fred_api_key
from utils import default_logger as logger
import pandas as pd


class FredWrapper(Fred):
    """
    A wrapper around the fredapi.Fred class that automatically
    retrieves the API key from the configuration if not provided.
    """

    def __init__(self, api_key: str = None, **kwargs):
        if api_key is None:
            logger.info("No API key provided, fetching from config...")
            api_key = get_fred_api_key()
        else:
            logger.info("Using provided API key.")

        super().__init__(api_key, **kwargs)
        logger.info("FredWrapper initialized successfully")

    def get_latest_release(self, series_id):
        data = self.get_series_latest_release(series_id)
        # data.name = series_id
        data = pd.DataFrame(data)
        data.index.name = "Date"
        data.columns = [series_id]

        return data
