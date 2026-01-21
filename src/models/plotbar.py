'''
Plot frequency of residual of COP
'''
import matplotlib.pyplot as plt
import pandas as pd
import fhgcd_plots.main as fhgCD
import matplotlib.dates as mdates



#df = pd.read_csv('combined_simulation_results.csv',sep=',')
df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
df2 = pd.read_csv('simulation_results.csv',sep=',')

#fhgCD.set_matplotlib_style("scientific", "official")

df1_10 = df1.iloc[::10]
# Absolute error
error_abs = df2['COP'].values - df1_10['Column4'].values

fig, ax = plt.subplots(figsize=(8, 4))

ax.hist(error_abs, bins='fd',rwidth=0.8,label='Frequency')

ax.set_xlabel('Residual (COP)')
ax.set_ylabel('Frequency')
ax.set_title('Frequency distribution of residuals of COP')
ax.grid(True)
ax.legend()

plt.tight_layout()
plt.show()


