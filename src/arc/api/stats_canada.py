from __future__ import annotations

from typing import Optional, Iterable
import itertools
import pandas as pd
import requests

from arc.utils import default_logger as logger
from arc.database.helpers import upsert_series, bulk_insert_economic
from arc.database.core import session_scope
from arc.database import models as m

# --------------------------------------------------------------------------- #
#  ENDPOINT CANDIDATES
# --------------------------------------------------------------------------- #
_REST = "https://www150.statcan.gc.ca/t1/wds/rest"
_LEGACY = "https://www150.statcan.gc.ca/t1/wds/en/gr1"

# (path-suffix, expects_json)
_ENDPOINTS: list[tuple[str, bool]] = [
    # newest REST route (Jan-2025 guide)
    ("/getDataFromVectorsByVectorIds?vectorIds={vec}", True),
    # 2024 vintage
    ("?getDataObjectsFromVectors&vectorIds={vec}", True),
    # really old CSV hack (still live for some vectors)
    ("/{vec}?format=CSV", False),
]


# --------------------------------------------------------------------------- #
#  WRAPPER
# --------------------------------------------------------------------------- #
class StatsCanWrapper:
    """
    get_vector("v41690973") → tidy DataFrame (Date index, 1 col = vector-ID)
    with **automatic** SQLite caching & multi-endpoint fall-back.
    """

    def get_vector(self, vector_id: str, *, cache: bool = True) -> pd.DataFrame:
        vector_id = vector_id.lower().strip()

        # ---- 1. SQLite cache ------------------------------------------------
        if cache:
            cached = self._load_from_cache(vector_id)
            if cached is not None:
                logger.info("StatsCan: cache hit for %s", vector_id)
                return cached

        # ---- 2. hit StatCan WDS -------------------------------------------
        for base, (suffix, as_json) in itertools.product((_REST, _LEGACY), _ENDPOINTS):
            url = f"{base}{suffix.format(vec=vector_id)}"
            try:
                logger.debug("StatsCan: probing %s", url)
                resp = requests.get(url, timeout=30)
                resp.raise_for_status()
            except requests.HTTPError as e:
                if e.response is not None and e.response.status_code == 404:
                    continue  # try next candidate
                raise  # other network problems → bubble up

            # ---- parse payload --------------------------------------------
            if as_json:
                payload = resp.json()
                status = payload[0].get("status", payload[0].get("responseStatusCode"))
                if status != 0:  # 0 = Success
                    msg = payload[0].get("message", "unknown WDS error")
                    raise RuntimeError(f"StatsCan WDS error {status}: {msg}")

                rows = payload[1]["vectorData"]
                df = (
                    pd.DataFrame(rows)
                    .rename(columns={"refPer": "Date", "value": vector_id})
                    .assign(Date=lambda d: pd.to_datetime(d["Date"]))
                    .set_index("Date")
                    .astype({vector_id: float})
                )
            else:  # CSV fallback
                df = (
                    pd.read_csv(url)
                    .rename(columns={"REF_DATE": "Date", "VALUE": vector_id})
                    .assign(Date=lambda d: pd.to_datetime(d["Date"]))
                    .set_index("Date")
                    .astype({vector_id: float})
                )

            # success – stop probing
            break
        else:
            raise RuntimeError(
                f"All StatCan endpoints returned 404 for vector '{vector_id}'. "
                "Check the ID at https://www150.statcan.gc.ca/t1/tbl1/en/tv.action"
            )

        # ---- 3. persist to cache ------------------------------------------
        if cache:
            self._write_to_cache(vector_id, df)

        return df

    # ------------------------------------------------------------------ #
    #  cache helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _load_from_cache(vector_id: str) -> Optional[pd.DataFrame]:
        with session_scope() as s:
            series = s.query(m.EconomicSeries).filter_by(series_id=vector_id).first()
            if not series:
                return None
            rows = (
                s.query(m.EconomicData)
                .filter_by(economic_series_id=series.id)
                .order_by(m.EconomicData.date)
                .all()
            )
            return None if not rows else series.to_dataframe(rows)

    @staticmethod
    def _write_to_cache(vector_id: str, df: pd.DataFrame) -> None:
        pk = upsert_series(vector_id, title=vector_id)
        bulk_insert_economic(pk, df)
        logger.info("StatsCan: cached %s (%d rows)", vector_id, len(df))
