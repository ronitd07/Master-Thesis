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
#df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
#df1_10 = df1.iloc[::10]
#df2 = pd.read_csv('charmap_simulation_results8.csv',sep=',')

df9 = pd.read_csv('charmap_simulation_results9.csv',sep=',')
df8 = pd.read_csv('charmap_simulation_results8.csv',sep=',')
df = pd.concat([df8, df9])

# Filter for COP > 2.4
df2_filtered = df[(df['cop_given'] > 2.4) & (df['cop'].notna())]

# Recalculate R²
R2 = r2_score(df2_filtered['cop_given'], df2_filtered['cop'])
print("R^2 =", R2)

# Recalculate standard deviation of absolute error
error_abs = np.abs(df2_filtered['cop'] - df2_filtered['cop_given'])
std_error = np.std(error_abs, ddof=1)
print("Standard deviation of absolute error:", std_error)

# Plot
fig, ax = plt.subplots(figsize=(8, 4))
x = np.linspace(2, df2_filtered['cop_given'].max(), 100)
y = x.copy()

ax.plot(df2_filtered['cop_given'], df2_filtered['cop'], 'o',
        label=f'$R^2$ = {R2:.3f}, $\\sigma$ = {std_error:.3f}')
ax.plot(x, y)

ax.set_ylim(2.2, df2_filtered['cop_given'].max())
ax.set_xlim(2.2, df2_filtered['cop_given'].max())

ax.set_xlabel('Real COP')
ax.set_ylabel('Simulated COP')
ax.set_title("Comparison of Simulated COP and Real COP (COP > 2.4)")
ax.grid(True)
ax.legend(fontsize=12)

plt.tight_layout()
plt.savefig("COP_compare_filtered.png", dpi=300, bbox_inches="tight")
plt.show()


