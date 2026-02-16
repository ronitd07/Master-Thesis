'''
Compare COP simulated and given after using default charmap for compressor and evaporator
Calculate RMSE and MAPE
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import fhgcd_plots.main as fhgCD
import numpy as np

df = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data

df['Column1'] = pd.to_datetime(df['Column1'])


#fhgCD.set_matplotlib_style("scientific", "official")
fig, ax = plt.subplots(figsize=(10, 4))

ax.scatter(df['Column1'], df['Column23'],marker = 'x',
         label='Q load over time')



# Monthly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

# Improve readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

ax.set_xlabel('Month')
ax.set_ylabel('Q_load (MW)')
ax.legend()
ax.grid(True)
plt.savefig("Q_load.png", dpi=300, bbox_inches="tight")
plt.show()