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
df = pd.read_csv('charmap_simulation_results6.csv',sep=',')
df2 = pd.read_csv('compressor_results1.csv',sep=',')
'''
#Determine standard deviation sigma
mask = df['eta1'].notna()

error_abs = df2.loc[mask, 'Comp1 eff'].values - df.loc[mask, 'eta1'].values
std_error = np.std(error_abs, ddof=1)
print("Standard deviation of absolute error:", std_error)
'''
x = df['cp1']
y = df1['Column37'][::10]

R2 = r2_score(y, x)
print("R^2 =", R2)

#Determine standard deviation sigma
error_abs = np.abs(x - y)
std_error = np.std(error_abs, ddof=1)
print("Standard deviation of absolute error:", std_error)

fig, ax = plt.subplots(figsize=(8, 4))
x0=np.linspace(1000,3500,100)
y0=np.linspace(1000,3500,100)

ax.scatter(df['cp1'], df1['Column37'][::10],marker = 'o')
ax.plot(x0,y0)

#ax.set_ylim(2, 3.5)
#ax.set_xlim(2, 3.5)


ax.set_xlabel('Simulated power compressor 1 (kW)')
ax.set_ylabel('Real power compressor 1 (kW)')
ax.set_title(f"Comparison of Simulated and Real Power Compressor 1")
ax.grid(True)


fig, ax1 = plt.subplots(figsize=(8, 4))
x=np.linspace(1500,3700,100)
y=np.linspace(1500,3700,100)

ax1.scatter(df['cp2'], df1['Column38'][::10],marker = 'o')
ax1.plot(x,y)

#ax.set_ylim(2, 3.5)
#ax.set_xlim(2, 3.5)


ax1.set_xlabel('Simulated power compressor 2 (kW)')
ax1.set_ylabel('Real power compressor 2 (kW)')
ax1.set_title(f"Comparison of Simulated and Real power Compressor 2")
ax1.grid(True)


plt.tight_layout()
#plt.savefig("COP compare.png", dpi=300, bbox_inches="tight")
plt.show()


