from __future__ import annotations

import pandas as pd
from fredapi import Fred

from arc.config import get_fred_api_key
from arc.utils import default_logger as logger
from arc.database.core import session_scope
from arc.database import models as m
from arc.database.helpers import upsert_series, bulk_insert_economic


class FredWrapper(Fred):
    """
    Thin wrapper around `fredapi.Fred` that adds:
      • automatic API-key loading from env
      • SQLite caching (read + write)
    """

    # ------------------------------------------------------------------ #
    #  Construction
    # ------------------------------------------------------------------ #
    def __init__(self, api_key: str | None = None, **kwargs):
        if api_key is None:
            api_key = get_fred_api_key()
            logger.info("FredWrapper: pulled API key from env")
        super().__init__(api_key, **kwargs)
        logger.info("FredWrapper initialised")

    # ------------------------------------------------------------------ #
    #  Public helpers
    # ------------------------------------------------------------------ #
    def get_latest_release(self, series_id: str, cache: bool = True) -> pd.DataFrame:
        """
        Return the latest-vintage time-series for `series_id` as a DataFrame.
        If `cache=True`, try SQLite first; otherwise hit FRED and persist.
        """
        if cache:
            df = self._load_from_cache(series_id)
            if df is not None:
                logger.info("Loaded %s from SQLite cache", series_id)
                return df

        # --- cache miss: fetch from remote --------------------------------
        raw = self.get_series_latest_release(series_id)
        df = pd.DataFrame(raw, columns=[series_id]).rename_axis("Date")

        if cache:
            self._write_to_cache(series_id, df)

        return df

    # ------------------------------------------------------------------ #
    #  Internal helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _load_from_cache(series_id: str) -> pd.DataFrame | None:
        """
        Try to hydrate a DataFrame for `series_id` from the relational cache.
        Return None on miss.
        """
        with session_scope() as s:
            series = s.query(m.EconomicSeries).filter_by(series_id=series_id).first()
            if not series:
                return None

            rows = (
                s.query(m.EconomicData)
                .filter_by(economic_series_id=series.id)
                .order_by(m.EconomicData.date)
                .all()
            )
            if not rows:
                return None

            return series.to_dataframe(rows)

    @staticmethod
    def _write_to_cache(series_id: str, df: pd.DataFrame) -> None:
        """
        Persist the DataFrame into `economic_series` + `economic_data`.
        """
        pk = upsert_series(series_id)
        bulk_insert_economic(pk, df)
        logger.info("Cached %s into SQLite (%d rows)", series_id, len(df))
