from fredapi import Fred
import pandas as pd

from arc.config import get_fred_api_key
from arc.utils import default_logger as logger
from arc.database.core import session_scope
from arc.database import models as m


class FredWrapper(Fred):
    """
    A wrapper around the fredapi.Fred class that automatically
    retrieves the API key from the configuration if not provided.
    """

    def __init__(self, api_key: str = None, **kwargs):
        if api_key is None:
            logger.info("No API key provided, fetching from arc.config...")
            api_key = get_fred_api_key()
        else:
            logger.info("Using provided API key.")

        super().__init__(api_key, **kwargs)
        logger.info("FredWrapper initialized successfully")

    def get_latest_release(self, series_id: str, cache: bool = True):
        # if cache = True, check if we have data cached in local db and return
        if cache:
            with session_scope() as s:
                row = (
                    s.query(m.EconomicData)
                    .join(m.EconomicSeries)
                    .filter(m.EconomicSeries.series_id == series_id)
                    .order_by(m.EconomicData.date.desc())
                    .first()
                )

                if row:
                    logger.info("Loaded %s from SQLite cache", series_id)
                    return row.to_dataframe()

        # if we don't have data in local db, network request
        data = self.get_series_latest_release(series_id)
        df = pd.DataFrame(data, columns=[series_id]).rename_axis("Date")

        if cache:
            with session_scope() as s:
                # insert into local db placeholder
                pass

        return df
