from yfinance import Tickers
from yfinance.utils import auto_adjust as adj
from utils import default_logger as logger
# import pandas as pd


class YFWrapper():
    """
    A wrapper around the yfinance.Tickers class
    """

    def __init__(self):
        self.tickers_obj = []
        logger.info("yFinance wrapper initialized succesfully")

    def get_data(
        self,
        tickers: list | str,
        period="1mo",
        interval="1d",
        start=None,
        end=None,
        prepost=False,
        actions=True,
        auto_adjust=True,
        repair=False,
        proxy=None,
        threads=True,
        group_by='column',
        progress=True,
        timeout=10,
        **kwargs
    ):

        tick = Tickers(tickers)
        logger.info("Tickers object initialized succesfully")
        self.tickers_obj.append(tick)

        data = tick.download(
            period=period,
            interval=interval,
            start=start,
            end=end,
            prepost=prepost,
            actions=actions,
            auto_adjust=False,
            repair=repair,
            proxy=proxy,
            threads=threads,
            group_by=group_by,
            progress=progress,
            timeout=timeout,
            **kwargs
        )

        # self auto-adjust so that unadjusted is always cached locally
        # this is how adjustment was applied in yfinance source code
        # https://github.com/ranaroussi/yfinance/blob/main/yfinance/scrapers/history.py#L416
        if auto_adjust:
            try:
                data = adj(data)

            except Exception as e:
                err_msg = "auto_adjust failed with %s" % e

        return data



# base_yf = YFWrapper()
