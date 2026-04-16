'''
Plot frequency of residual of COP, R^2 and standard deviation
'''
import matplotlib.pyplot as plt
import pandas as pd
#import fhgcd_plots.main as fhgCD
import matplotlib.dates as mdates
import numpy as np
from sklearn.metrics import r2_score



df = pd.read_csv('charmap_simulation_results_RMSE (2).csv',sep=',')
#df = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
#df1_10 = df.iloc[::10]
#df9 = pd.read_csv('charmap_simulation_results9.csv',sep=',')
#df8 = pd.read_csv('charmap_simulation_results8.csv',sep=',')
#df = pd.concat([df8, df9])

#fhgCD.set_matplotlib_style("scientific", "official")


#Determine R^2 coeficient of Determination


#mask = df2['cop'].notna()
#R2 = r2_score(df1['Column32'][::10].dropna(), df2['cop'].dropna())

R2 = r2_score(df['cop_given'].dropna(), df['cop'].dropna())
print("R^2 =", R2)

#Determine standard deviation sigma
error_abs = np.abs(df['cop'].dropna().values - df['cop_given'].dropna().values)
std_error = np.std(error_abs, ddof=1)
print("Standard deviation of absolute error:", std_error)

fig, ax = plt.subplots(figsize=(8, 4))
x=np.linspace(0,5,100)
y=np.linspace(0,5,100)

#df2['speedline_round'] = df2['Speed line X'].round(3)

#for speed, group in df2.groupby('speedline_round'):
#    ax.plot(group['cop_given'], group['cop'], 'o', label=f'Speedline {speed}')

ax.plot(df['cop_given'].dropna(), df['cop'].dropna(), 'o',label = f'$R^2$ = {R2:.3f}, $\\sigma$ = {std_error:.3f}')
ax.plot(x,y)

ax.set_ylim(2, 3.5)
ax.set_xlim(2, 3.5)


ax.set_xlabel('Real COP')
ax.set_ylabel('Simulated COP')
ax.set_title(f"Comparison of Simulated COP and real COP")
ax.grid(True)
ax.legend(fontsize=20)

plt.tight_layout()
plt.savefig("COP compare.png", dpi=300, bbox_inches="tight")
plt.show()


