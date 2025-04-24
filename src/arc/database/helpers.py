from datetime import date
import pandas as pd
from .core import session_scope
from . import models as m


def upsert_series(series_id: str, title: str | None = None) -> int:
    with session_scope() as s:
        row = s.query(m.EconomicSeries).filter_by(series_id=series_id).first()
        if row:
            return row.id
        row = m.EconomicSeries(series_id=series_id, title=title or series_id)
        s.add(row)
        s.flush()  # get autoincrement id
        return row.id


def bulk_insert_economic(series_pk: int, df: pd.DataFrame):
    # df.index is dates, df.iloc[:,0] is value
    records = [
        m.EconomicData(
            economic_series_id=series_pk,
            date=dt.date() if isinstance(dt, date) else dt,
            value=float(val),
        )
        for dt, val in df.iloc[:, 0].items()
    ]
    with session_scope() as s:
        s.bulk_save_objects(records, return_defaults=False)
