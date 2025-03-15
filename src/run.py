from api import FredWrapper, YFWrapper
import matplotlib.pyplot as plt
# import pandas as pd


fred = FredWrapper()
yf = YFWrapper()

scpi_seriesid = "CPIAUCSL"
cpi_seriesid = "CPIAUCNS"

cpi_sa = fred.get_series_latest_release(scpi_seriesid)["2018":]
cpi_pct = cpi_sa.pct_change(periods=12) * 100
print(cpi_pct)

tickers = ["msft", "nvda"]
stk = yf.get_data(tickers, start=cpi_pct.index[0], interval="1mo")
prices = stk["Close"]
print(prices)

print(prices.columns)
# plt.plot(cpi_pct)
# plt.show()
