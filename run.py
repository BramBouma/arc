from api import base_fred as fred
import matplotlib.pyplot as plt
# import pandas as pd


scpi_seriesid = "CPIAUCSL"
cpi_seriesid = "CPIAUCNS"

cpi_sa = fred.get_series_latest_release(scpi_seriesid)["2018":]
cpi_pct = cpi_sa.pct_change(periods=12) * 100
print(cpi_pct)
plt.plot(cpi_pct)
plt.show()
