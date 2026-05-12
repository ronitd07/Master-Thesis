'''
Plot frequency of residual of COP, R^2 and standard deviation
'''
import matplotlib.pyplot as plt
import pandas as pd
#import fhgcd_plots.main as fhgCD
import matplotlib.dates as mdates
import numpy as np



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

fig, ax = plt.subplots(figsize=(8, 4))
x=np.linspace(20,60,100)
y=np.linspace(20,60,100)

ax.scatter(df['igva1'], df2['igva1'][::10],marker = 'o')
ax.plot(x,y)

#ax.set_ylim(2, 3.5)
#ax.set_xlim(2, 3.5)


ax.set_xlabel('Simulated igva compressor 1 (°)')
ax.set_ylabel('Real igva compressor 1 (°)')
ax.set_title(f"Comparison of Simulated and Real igva Compressor 1")
ax.grid(True)


fig, ax1 = plt.subplots(figsize=(8, 4))
x=np.linspace(-5,35,100)
y=np.linspace(-5,35,100)

ax1.scatter(df['igva2'], df2['igva2'][::10],marker = 'o')
ax1.plot(x,y)

#ax.set_ylim(2, 3.5)
#ax.set_xlim(2, 3.5)


ax1.set_xlabel('Simulated igva compressor 2 (°)')
ax1.set_ylabel('Real igva compressor 2 (°)')
ax1.set_title(f"Comparison of Simulated and Real igva Compressor 2")
ax1.grid(True)


plt.tight_layout()
#plt.savefig("COP compare.png", dpi=300, bbox_inches="tight")
plt.show()


