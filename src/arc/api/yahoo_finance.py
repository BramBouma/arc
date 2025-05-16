from __future__ import annotations

from datetime import date
from typing import Iterable, List

import pandas as pd
from yfinance import Tickers
from yfinance.utils import auto_adjust as adj

from arc.utils import default_logger as logger
from arc.database.helpers import (
    upsert_ticker,
    bulk_insert_prices,
    load_prices,
)


class YFWrapper:
    """
    Thin wrapper around yfinance that adds SQLite caching.
    """

    # ------------------------------------------------------------------ #
    #  Construction
    # ------------------------------------------------------------------ #
    def __init__(self) -> None:
        self._live_tickers: List[Tickers] = []
        logger.info("YFWrapper initialised")

    # ------------------------------------------------------------------ #
    #  Public
    # ------------------------------------------------------------------ #
    def get_data(
        self,
        tickers: list[str] | str,
        *,
        period: str = "1mo",
        interval: str = "1d",
        start: str | None = None,
        end: str | None = None,
        cache: bool = True,
        columns: Iterable[str] | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Return OHLCV data for one or many tickers.
        `columns` lets callers down-select before return.
        """
        # yfinance normalises to upper-case
        tickers_iter = (
            [t.upper() for t in tickers]
            if isinstance(tickers, list)
            else [tickers.upper()]
        )

        dfs: list[pd.DataFrame] = []

        # -------------------------------------------------------------- #
        # 1. Try cache per ticker
        # -------------------------------------------------------------- #
        if cache:
            for t in tickers_iter:
                pk = upsert_ticker(t)
                df_cached = load_prices(
                    pk,
                    interval,
                    _to_date(start),
                    _to_date(end),
                    columns,
                )
                if df_cached is not None:
                    logger.info("Loaded %s %s from SQLite cache", t, interval)
                    dfs.append(df_cached.assign(Ticker=t))
                else:
                    logger.info("Cache miss for %s – will fetch", t)

        missing = [
            t
            for t in tickers_iter
            if t.upper() not in {df["Ticker"].iloc[0] for df in dfs}
        ]

        # -------------------------------------------------------------- #
        # 2. Fetch any missing tickers from yfinance
        # -------------------------------------------------------------- #
        if missing:
            tick_obj = Tickers(" ".join(missing))
            self._live_tickers.append(tick_obj)

            df_live = tick_obj.download(
                period=period,
                interval=interval,
                start=start,
                end=end,
                auto_adjust=False,
                progress=False,
                **kwargs,
            )

            # yfinance returns MultiIndex columns when >1 ticker
            if isinstance(df_live.columns, pd.MultiIndex):
                stack = []
                for t in missing:
                    part = df_live.xs(t.upper(), level=1, axis=1)
                    part.columns = [c.title() for c in part.columns]  # unify
                    stack.append(part.assign(Ticker=t.upper()))
                    # ---- persist ------------------------------------------------
                    if cache:
                        pk = upsert_ticker(t)
                        bulk_insert_prices(pk, interval, part)
                dfs.extend(stack)

            else:
                df_live.columns = [c.title() for c in df_live.columns]
                t = missing[0]
                dfs.append(df_live.assign(Ticker=t))

                if cache:
                    pk = upsert_ticker(t)
                    bulk_insert_prices(pk, interval, df_live)

        # -------------------------------------------------------------- #
        # 3. Return concatenated DataFrame with MultiIndex columns
        # -------------------------------------------------------------- #
        if not dfs:
            raise RuntimeError("No data returned from cache nor yfinance")

        out = (
            pd.concat(dfs)
            .set_index("Ticker", append=True)
            .swaplevel(axis=0)
            .sort_index(axis=0, level=1)
            .sort_index(axis=1)
        )  # rows: date x ticker -> columns normalised

        if columns is not None:
            out = out[columns]

        return out


# ------------------------------------------------------------------ #
#  Utility
# ------------------------------------------------------------------ #
def _to_date(s: str | None) -> date | None:
    if s is None:
        return None
    return pd.to_datetime(s).date()
