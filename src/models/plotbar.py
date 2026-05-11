'''
Plot frequency of residual of COP
'''
import matplotlib.pyplot as plt
import pandas as pd
import fhgcd_plots.main as fhgCD
import matplotlib.dates as mdates
import numpy as np



#df = pd.read_csv('charmap_simulation_results6_count.csv',sep=',')
df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
#df2 = pd.read_csv('charmap_simulation_results6full.csv',sep=',')
df2 = pd.read_csv('compressor_results1.csv',sep=',')

fhgCD.set_matplotlib_style("darkgrid", "official")

df1_10 = df1.iloc[::10]
df2_10 = df2.iloc[::10]
# Absolute error
error_abs = df2['cop'].values - df2['cop_given'].values


fig, ax = plt.subplots(figsize=(8, 4))

ax.hist(error_abs, bins='fd',rwidth=0.8,label='Frequency')

ax.set_xlabel('Residual (COP)')
ax.set_ylabel('Frequency')
#ax.set_title('Frequency distribution of residuals of COP')
ax.grid(True, axis="y", alpha=0.3, zorder=0)
ax.legend()
ax.set_xlim(-0.5,0.5)
plt.savefig("COP residual barplot.png", dpi=300, bbox_inches="tight")
plt.tight_layout()
plt.show()


