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

ax.scatter(df['datetime'], df['Mass flow comp1'],
         label='Mass flow compressor 1')
ax.scatter(df['datetime'], df['Mass flow comp2'],
         label='Mass flow Compressor 2')

# Monthly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

# Improve readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

ax.set_xlabel('Months')
ax.set_ylabel('Mass flow (kg/s)')
ax.legend()
ax.grid(True)
plt.savefig("mass flows compressors.png", dpi=300, bbox_inches="tight")

plt.tight_layout()
plt.show()
