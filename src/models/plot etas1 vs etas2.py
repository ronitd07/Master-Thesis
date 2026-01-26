'''
- Plot eta_s vs pr of compressor 1 and 2
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import fhgcd_plots.main as fhgCD
import numpy as np


df = pd.read_csv('simulation_results.csv',sep=',')

df['datetime'] = pd.to_datetime(df['datetime'])

#fhgCD.set_matplotlib_style("scientific", "official")
fig, ax = plt.subplots(figsize=(10, 4))

ax.scatter(df['datetime'], df['Efficiency comp1'],
         label='Efficiency Compressor 1')
ax.scatter(df['datetime'], df['Efficiency comp2'],
         label='Efficiency Compressor 2')

# Monthly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

# Improve readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')


ax.set_xlabel('Month')
ax.set_ylabel('efficiency')
ax.legend()
ax.grid(True)

plt.tight_layout()
plt.show()
