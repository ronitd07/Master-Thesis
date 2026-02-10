'''
Plot frequency of residual of COP, R^2 and standard deviation
'''
import matplotlib.pyplot as plt
import pandas as pd
#import fhgcd_plots.main as fhgCD
import matplotlib.dates as mdates
import numpy as np

df = pd.read_csv('charmap_simulation_results1.csv',sep=',')

#fhgCD.set_matplotlib_style("scientific", "official")



fig, ax = plt.subplots(figsize=(8, 4))
ax.scatter(df['m1'], df['igva1'],marker = 'x' ,label = 'igva Compressor 1' )
ax.scatter(df['m2'], df['igva2'],marker = 'x', label = 'igva Compressor 2' )


ax.set_xlabel('Mass flow (kg/s)')
ax.set_ylabel('Igva (°)')
ax.set_title(f"Effect of mass flow on inlet guide vane angle")
ax.grid(True)
ax.legend()

plt.tight_layout()
plt.show()


