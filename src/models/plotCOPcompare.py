'''
Comparing COP with given data in excel and the COP calculated from excel with load and compressor power
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import fhgcd_plots.main as fhgCD

df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
#df2 = pd.read_csv('full_simulation_results.csv',sep=',')


#df1 = pd.read_excel('data/process_data/Data 50.xlsx', sheet_name="Tabelle1", header=0,skiprows=range(1, 5)) #Load profile data
df2 = pd.read_csv('full_simulation_results.csv',sep=',')

df1['Column1'] = pd.to_datetime(df1['Column1'])


#fhgCD.set_matplotlib_style("scientific", "official")
fig1, ax = plt.subplots(figsize=(10, 4))

ax.plot(df1['Column1'], df1['Column4'],
         label='COP given')
ax.plot(df1['Column1'], df1['Column32'],
        label='COP cal from data given in excel')

# Monthly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

# Improve readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

ax.set_xlabel('Month')
ax.set_ylabel('COP')
ax.legend()
ax.grid(True)
plt.show()