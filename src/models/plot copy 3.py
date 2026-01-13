'''
Temp lift vs COP plot
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import fhgcd_plots.main as fhgCD

df1 = pd.read_excel('data/process_data/Manheim_data_cleaned3.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
df2 = pd.read_csv('full_simulation_results.csv',sep=',')

df1['Column1'] = pd.to_datetime(df1['Column1'])
df2['datetime'] = pd.to_datetime(df2['datetime'])

fhgCD.set_matplotlib_style("greengrid", "rainbow")
fig, ax = plt.subplots(figsize=(10, 4))

ax.plot(df2['Temp difference'], df2['COP'],
        marker='o', linestyle='-', label='COP')



ax.set_xlabel('Temp lift (°C)')
ax.set_ylabel('COP')
ax.legend()
ax.grid(True)

plt.tight_layout()
plt.show()