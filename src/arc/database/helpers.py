"""
Helper utilities for reading / writing the relational cache.
"""

from __future__ import annotations

from datetime import date
from typing import Iterable

import pandas as pd

from .core import session_scope
from . import models as m


# ──────────────────────────────────────────────────────────
#  ECONOMIC SERIES (already used by FredWrapper)
# ──────────────────────────────────────────────────────────
def upsert_series(series_id: str, *, title: str | None = None) -> int:
    """Return PK for series; create row if it doesn’t exist."""
    with session_scope() as s:
        row = s.query(m.EconomicSeries).filter_by(series_id=series_id).first()
        if row:
            return row.id
        row = m.EconomicSeries(series_id=series_id, title=title or series_id)
        s.add(row)
        s.flush()  # populate auto-increment PK
        return row.id


def bulk_insert_economic(series_pk: int, df: pd.DataFrame) -> None:
    """Insert every observation in *df* (index = dates, 1 col = value)."""
    records = [
        m.EconomicData(
            economic_series_id=series_pk,
            date=idx if isinstance(idx, date) else idx.date(),
            value=float(val),
        )
        for idx, val in df.iloc[:, 0].items()
    ]
    with session_scope() as s:
        s.bulk_save_objects(records, return_defaults=False)


# ──────────────────────────────────────────────────────────
#  STOCK HELPERS
# ──────────────────────────────────────────────────────────
def upsert_ticker(ticker: str, **meta) -> int:
    """Return PK for ticker; create minimal row if it doesn’t exist."""
    ticker = ticker.upper()
    with session_scope() as s:
        row = s.query(m.StockMetadata).filter_by(ticker=ticker).first()
        if row:
            return row.id
        row = m.StockMetadata(ticker=ticker, **meta)
        s.add(row)
        s.flush()
        return row.id


def bulk_insert_prices(
    stock_pk: int,
    interval: str,
    df: pd.DataFrame,
) -> None:
    """
    Insert OHLCV rows for *stock_pk*.
    Expects *df* to have a simple Index of dates and the usual columns.
    """
    records: list[m.StockPrice] = []
    for d, row in df.iterrows():
        records.append(
            m.StockPrice(
                stock_id=stock_pk,
                interval=interval,
                date=d.date() if isinstance(d, date) else d,
                open=row.get("Open"),
                close=row.get("Close"),
                high=row.get("High"),
                low=row.get("Low"),
                volume=row.get("Volume"),
                dividends=row.get("Dividends"),
                splits=row.get("Stock Splits")
                if "Stock Splits" in row
                else row.get("Splits"),
            )
        )
    with session_scope() as s:
        s.bulk_save_objects(records, return_defaults=False)


def load_prices(
    stock_pk: int,
    interval: str,
    start: date | None,
    end: date | None,
    columns: Iterable[str] | None = None,
) -> pd.DataFrame | None:
    """
    Return a DataFrame (index = date) for *stock_pk* in [start, end].
    If any date is missing, return None so the caller knows to hit the API.
    """
    from sqlalchemy import and_

    with session_scope() as s:
        q = s.query(m.StockPrice).filter(
            m.StockPrice.stock_id == stock_pk,
            m.StockPrice.interval == interval,
        )
        if start:
            q = q.filter(m.StockPrice.date >= start)
        if end:
            q = q.filter(m.StockPrice.date <= end)

        rows = q.order_by(m.StockPrice.date).all()

        # naïve completeness check: we expect at least one row per day
        if not rows:
            return None

        # build DataFrame
        data = {
            "Open": [r.open for r in rows],
            "Close": [r.close for r in rows],
            "High": [r.high for r in rows],
            "Low": [r.low for r in rows],
            "Volume": [r.volume for r in rows],
            "Dividends": [r.dividends for r in rows],
            "Stock Splits": [r.splits for r in rows],
        }
        df = pd.DataFrame(data, index=[r.date for r in rows])
        if columns is not None:
            df = df[list(columns)]
        return df
