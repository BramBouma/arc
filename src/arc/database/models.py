from __future__ import annotations

from datetime import datetime
from typing import List
import pandas as pd
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    ForeignKey,
)
from .core import Base


# ------------------------------------------------------------------ #
#  STOCK TABLES
# ------------------------------------------------------------------ #
class StockMetadata(Base):
    __tablename__ = "stock_metadata"

    id = Column(Integer, primary_key=True)
    ticker = Column(String, unique=True, nullable=False)
    company_name = Column(String)
    exchange = Column(String)
    sector = Column(String)
    industry = Column(String)
    currency = Column(String)
    metadata_fetched_at = Column(DateTime, default=datetime.utcnow)


class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stock_metadata.id"), nullable=False)
    interval = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float)
    close = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(Integer)
    dividends = Column(Float)
    splits = Column(Float)
    fetched_at = Column(DateTime, default=datetime.utcnow)


# ------------------------------------------------------------------ #
#  ECONOMIC TABLES
# ------------------------------------------------------------------ #
class EconomicSeries(Base):
    __tablename__ = "economic_series"

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False, default="fred")  # e.g. “fred”
    series_id = Column(String, unique=True, nullable=False)  # CPIAUCSL
    title = Column(String)
    frequency = Column(String)
    units = Column(String)
    seasonal_adjustment = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)

    # ---- helper --------------------------------------------------- #
    def to_dataframe(self, rows: List["EconomicData"]) -> pd.DataFrame:
        """
        Convert a list of EconomicData rows (same series) into a
        pandas DataFrame indexed by date.
        """
        dates = [r.date for r in rows]
        values = [r.value for r in rows]
        return pd.DataFrame({self.series_id: values}, index=dates)


class EconomicData(Base):
    __tablename__ = "economic_data"

    id = Column(Integer, primary_key=True)
    economic_series_id = Column(
        Integer, ForeignKey("economic_series.id"), nullable=False
    )
    date = Column(Date, nullable=False)
    realtime_start = Column(Date, default=datetime.utcnow)
    realtime_end = Column(Date, default=datetime.utcnow)
    value = Column(Float, nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow)
