'''
Plot residual COP vs speedline
'''
import matplotlib.pyplot as plt
import pandas as pd
#import fhgcd_plots.main as fhgCD
import matplotlib.dates as mdates
import numpy as np
from sklearn.metrics import r2_score



#df = pd.read_csv('combined_simulation_results.csv',sep=',')
df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
df1_10 = df1.iloc[::10]
df2 = pd.read_csv('charmap_simulation_results_01042026.csv',sep=',')
#df2 = pd.read_csv('compressor_results1.csv',sep=',')

error_abs = np.abs(df2['cop'].dropna().values - df2['cop_given'].dropna().values)



fig, ax = plt.subplots(figsize=(8, 4))


ax.plot(df2['Speed line x'].dropna(), error_abs, 'o')


ax.set_xlabel('Speed line X')
ax.set_ylabel('COP Absolute error')
ax.set_title(f"Comparison of COP absolute error vs Speedline for Compressor 2")
ax.grid(True)

plt.tight_layout()
plt.savefig("COP residual vs speedline compressor 2.png", dpi=300, bbox_inches="tight")

fig, ax1 = plt.subplots(figsize=(8, 4))


ax1.plot(df2['Speed line X'].dropna(), error_abs, 'o')


ax1.set_xlabel('Speed line X')
ax1.set_ylabel('COP Absolute error')
ax1.set_title(f"Comparison of COP absolute error vs Speedline for Compressor 1")
ax1.grid(True)


plt.tight_layout()
plt.savefig("COP residual vs speedline compressor 1.png", dpi=300, bbox_inches="tight")
plt.show()


