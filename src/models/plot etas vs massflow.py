'''
- Plot eta_s vs pr of compressor 1 and 2
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import fhgcd_plots.main as fhgCD
import numpy as np


df = pd.read_csv('simulation_results.csv',sep=',')


#fhgCD.set_matplotlib_style("scientific", "official")
fig, ax = plt.subplots(figsize=(10, 4))

ax.scatter(df['Mass flow comp1'], df['Efficiency comp1'],
         label='Efficiency vs Mass flow Compressor 1')
ax.scatter(df['Mass flow comp2'], df['Efficiency comp2'],
         label='Efficiency vs Mass flow Compressor 2')


ax.set_xlabel('Mass flow (kg/s)')
ax.set_ylabel('efficiency')
ax.legend()
ax.grid(True)

plt.tight_layout()
plt.show()
