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
df1_10 = df1.iloc[::10]
df2 = pd.read_csv('charmap_simulation_results6.csv',sep=',')

#fhgCD.set_matplotlib_style("scientific", "official")


#Determine R^2 coeficient of Determination
from sklearn.metrics import r2_score

#mask = df2['cop'].notna()

R2 = r2_score(df1_10['Column47'], df2['eta2'])
print("R^2 =", R2)

#Determine standard deviation sigma
error_abs = np.abs(df1_10['Column47'].values - df2['eta2'].values)
std_error = np.std(error_abs, ddof=1)
print("Standard deviation of absolute error:", std_error)

fig, ax = plt.subplots(figsize=(8, 4))
x=np.linspace(0,1,100)
y=np.linspace(0,1,100)

ax.plot(df1_10['Column47'], df2['eta2'], 'o',label = f'$R^2$ = {R2:.3f}, $\\sigma$ = {std_error:.3f}')
ax.plot(x,y)

#ax.set_ylim(2, 3.5)
#ax.set_xlim(2, 3.5)


ax.set_xlabel('Real eta')
ax.set_ylabel('Simulated eta')
ax.set_title(f"Comparison of Simulated eta and real eta")
ax.grid(True)
ax.legend(fontsize=20)

plt.tight_layout()
plt.savefig("COP compare.png", dpi=300, bbox_inches="tight")
plt.show()


