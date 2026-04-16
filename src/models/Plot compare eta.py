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
eta_sim = df['eta1'].values
eta_real = df2['Comp1 eff'].values[::10]

mask = ~np.isnan(eta_sim)

eta_real = eta_real[mask]
eta_sim = eta_sim[mask]

R2 = r2_score(eta_sim, eta_real)
print("R^2 =", R2)

error_abs = np.abs(eta_real - eta_sim)
std_error = np.std(error_abs, ddof=1)
print("Standard deviation of absolute error:", std_error)

fig, ax = plt.subplots(figsize=(8, 4))
x=np.linspace(0.4,0.8,100)
y=np.linspace(0.4,0.8,100)

ax.scatter(df['eta1'], df2['Comp1 eff'][::10],marker = 'o',label = f'$R^2$ = {R2:.3f}, $\\sigma$ = {std_error:.3f}')
ax.plot(x,y)

#ax.set_ylim(2, 3.5)
#ax.set_xlim(2, 3.5)


ax.set_xlabel('Simulated eta compressor 1')
ax.set_ylabel('Real eta compressor 1')
ax.set_title(f"Comparison of Simulated and Real eta Compressor 1")
ax.grid(True)
ax.legend(fontsize=20)

eta_sim = df['eta2'].values
eta_real = df2['Comp2 eff'].values[::10]

mask = ~np.isnan(eta_sim)

eta_real = eta_real[mask]
eta_sim = eta_sim[mask]

R2 = r2_score(eta_sim, eta_real)
print("R^2 =", R2)

error_abs = np.abs(eta_real - eta_sim)
std_error = np.std(error_abs, ddof=1)
print("Standard deviation of absolute error:", std_error)

fig, ax1 = plt.subplots(figsize=(8, 4))
x=np.linspace(0.5,0.75,100)
y=np.linspace(0.5,0.75,100)

ax1.scatter(df['eta2'], df2['Comp2 eff'][::10],marker = 'o',label = f'$R^2$ = {R2:.3f}, $\\sigma$ = {std_error:.3f}')
ax1.plot(x,y)

#ax.set_ylim(2, 3.5)
#ax.set_xlim(2, 3.5)


ax1.set_xlabel('Simulated eta compressor 2')
ax1.set_ylabel('Real eta compressor 2')
ax1.set_title(f"Comparison of Simulated and Real eta Compressor 2")
ax1.grid(True)
ax1.legend(fontsize=20)


plt.tight_layout()
#plt.savefig("COP compare.png", dpi=300, bbox_inches="tight")
plt.show()


