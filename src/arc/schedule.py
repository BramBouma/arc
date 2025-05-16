"""
aps-scheduler stub: refreshes *all* cached data every night at 02:30 local.
stocks: whatever tickers are present in the db.
fred  : hard-coded watch-list for now.
"""

from datetime import datetime
from typing import Iterable
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from arc.database.core import _ENGINE, session_scope
from arc.database import models as m
from arc.api import YFWrapper, FredWrapper
from arc.utils import default_logger as log


# ────────────────────────────────────────────────────────────
#  helpers
# ────────────────────────────────────────────────────────────
def _all_tickers() -> Iterable[str]:
    with session_scope() as s:
        rows = s.query(m.StockMetadata.ticker).all()
        return [r.ticker for r in rows] or ["MSFT"]  # boot-strap


def refresh_stocks() -> None:
    tickers = _all_tickers()
    log.info("Scheduler: refreshing stocks %s", tickers)
    YFWrapper().get_data(tickers, period="6mo", interval="1d", cache=True)


_WATCH_FRED = ["CPIAUCSL", "FEDFUNDS", "UNRATE"]


def refresh_fred() -> None:
    fw = FredWrapper()
    for sid in _WATCH_FRED:
        log.info("Scheduler: refreshing FRED %s", sid)
        fw.get_latest_release(sid, cache=True)


# ────────────────────────────────────────────────────────────
#  entry-point
# ────────────────────────────────────────────────────────────
def launch(blocking: bool = True) -> None:
    jobstores = {"default": SQLAlchemyJobStore(engine=_ENGINE)}
    sched = BlockingScheduler(jobstores=jobstores, timezone="local")

    # run nightly at 02:30
    sched.add_job(refresh_stocks, "cron", hour=2, minute=30, id="stocks")
    sched.add_job(refresh_fred, "cron", hour=2, minute=35, id="fred")

    log.info("Starting scheduler -- press Ctrl-C to exit")
    if blocking:
        sched.start()
