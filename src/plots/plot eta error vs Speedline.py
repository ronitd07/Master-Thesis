'''
Plot frequency of residual of COP, R^2 and standard deviation
'''
import matplotlib.pyplot as plt
import pandas as pd
#import fhgcd_plots.main as fhgCD
import matplotlib.dates as mdates
import numpy as np
from sklearn.metrics import r2_score



#df = pd.read_csv('combined_simulation_results.csv',sep=',')
df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
df2 = pd.read_csv('charmap_simulation_results_count3.csv',sep=',')
df = pd.read_csv('compressor_results1.csv',sep=',')

mask = df2['eta1'].notna()
error_abs = np.abs(df2.loc[mask,'eta1'] - df.loc[mask,'Comp1 eff'])

#error_abs = np.abs(df2['eta1'].dropna().values - df['Comp1 eff'].dropna().values)



fig, ax = plt.subplots(figsize=(8, 4))


ax.plot(df2['Speed line X'].dropna(), error_abs, 'o')

ax.set_xlabel('Speed line X')
ax.set_ylabel('Efficiency Absolute error')
ax.set_title(f"Comparison of Efficiency absolute error vs Speedline for Compressor 1")
ax.grid(True)

mask = df2['eta2'].notna()
error_abs = np.abs(df2.loc[mask,'eta2'].values - df.loc[mask,'Comp2 eff'].values)

fig, ax1 = plt.subplots(figsize=(8, 4))


ax1.plot(df2['Speed line x'].dropna(), error_abs, 'o')

ax1.set_xlabel('Speed line x')
ax1.set_ylabel('Efficiency Absolute error')
ax1.set_title(f"Comparison of Efficiency absolute error vs Speedline for Compressor 2")
ax1.grid(True)


plt.tight_layout()
#plt.savefig("COP compare.png", dpi=300, bbox_inches="tight")
plt.show()


