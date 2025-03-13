from yfinance import Tickers
from utils import default_logger as logger


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

        return tick.download(
            period,
            interval,
            start,
            end,
            prepost,
            actions,
            auto_adjust,
            repair,
            proxy,
            threads,
            group_by,
            progress,
            timeout,
            **kwargs
        )


# base_yf = YFWrapper()
