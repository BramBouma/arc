import pandas as pd


def basic_chart(data: pd.DataFrame, type: str = "candle"):

    if type(data.columns) is pd.core.indexes.multi.MultiIndex:
        try:
            tickers = list(set(data.columns.get_level_values(level=1)))
        except Exception as e:
            raise e

    for tick in tickers:
        pass
