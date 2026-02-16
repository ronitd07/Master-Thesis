'''
Compare COP simulated and given after using default charmap for compressor and evaporator
Calculate RMSE and MAPE
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import fhgcd_plots.main as fhgCD
import numpy as np

df = pd.read_excel('cop comparison.xlsx', sheet_name="Sheet1", header=0) #Load profile data
df2 = pd.read_csv('charline2_simulation_results.csv',sep=',')



# RMSE
rmse = np.sqrt(np.mean((df2['cop'] - df2['cop_given'])**2))

# MAPE (in %)
mape = np.mean(np.abs((df2['cop'] - df2['cop_given']) / df2['cop_given'])) * 100

print(f"RMSE = {rmse:.3f}")
print(f"MAPE = {mape:.2f} %")

df2['datetime'] = pd.to_datetime(df2['datetime'])


#fhgCD.set_matplotlib_style("scientific", "official")
fig1, ax = plt.subplots(figsize=(10, 4))

df2['difference'] = df2['cop'] - df2['cop_given']

ax.scatter(df2['datetime'], df2['difference'],marker = 'x',
         label='COP diff')



# Monthly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

# Improve readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

ax.set_xlabel('Month')
ax.set_ylabel('COP Diff')
ax.legend()
ax.grid(True)
plt.savefig("cop difference.png", dpi=300, bbox_inches="tight")
plt.show()