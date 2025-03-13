from api import base_fred as fred, base_yf as yf
import matplotlib.pyplot as plt
# import pandas as pd


scpi_seriesid = "CPIAUCSL"
cpi_seriesid = "CPIAUCNS"

cpi_sa = fred.get_series_latest_release(scpi_seriesid)["2018":]
cpi_pct = cpi_sa.pct_change(periods=12) * 100
print(cpi_pct)

# print(cpi_pct.index)
# print(type(cpi_pct))
# print(type(cpi_pct.index))
# print(cpi_pct.co)

tickers = ["msft", "nvda"]
prices = yf.get_data(tickers, start=cpi_pct.index[0], end=cpi_pct.index[-1])
print(prices["Close"])

# plt.plot(cpi_pct)
# plt.show()
