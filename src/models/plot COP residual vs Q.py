'''
Plot residual of COP vs Q load
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
df2 = pd.read_csv('charmap_simulation_results6_test.csv',sep=',')
df = pd.read_csv('compressor_results1.csv',sep=',')

error_abs = np.abs(df2['cop_given'] - df2['cop'])



fig, ax = plt.subplots(figsize=(8, 4))


ax.plot(df2['Q'].dropna(), error_abs, 'o')

ax.set_xlabel('Load Q (MW)')
ax.set_ylabel('COP Residual')
ax.set_title(f"COP residual vs  Load")
ax.grid(True)


plt.tight_layout()
#plt.savefig("COP compare.png", dpi=300, bbox_inches="tight")
plt.show()


