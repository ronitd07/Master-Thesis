'''
Plot frequency of residual of COP, R^2 and standard deviation
'''
import matplotlib.pyplot as plt
import pandas as pd
import fhgcd_plots.main as fhgCD
import matplotlib.dates as mdates
import numpy as np



#df = pd.read_csv('combined_simulation_results.csv',sep=',')
df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
df1_10 = df1.iloc[::10]
df2 = pd.read_csv('simulation_results.csv',sep=',')

#fhgCD.set_matplotlib_style("scientific", "official")


#Determine R^2 coeficient of Determination
from sklearn.metrics import r2_score

R2 = r2_score(df1_10['Column4'], df2['COP'])
print("R^2 =", R2)

#Determine standard deviation sigma
error_abs = np.abs(df2['COP'].values - df1_10['Column4'].values)
std_error = np.std(error_abs, ddof=1)
print("Standard deviation of absolute error:", std_error)

fig, ax = plt.subplots(figsize=(8, 4))
x=np.linspace(0,5,100)
y=np.linspace(0,5,100)

ax.plot(df1_10['Column4'], df2['COP'], 'o',label = f"R² = {R2:.3f},σ = {std_error:.3f}" )
ax.plot(x,y)

ax.set_ylim(2, 4.5)
ax.set_xlim(2, 4.5)


ax.set_xlabel('Real COP')
ax.set_ylabel('Simulated COP')
ax.set_title(f"Comparison of Simulated COP and real COP")
ax.grid(True)
ax.legend(fontsize=20)

plt.tight_layout()
plt.show()


