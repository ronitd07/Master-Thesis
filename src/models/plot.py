'''
Absolute and relative error for COP plots
also compressor plots compare
'''
import matplotlib.pyplot as plt
import pandas as pd
import fhgcd_plots.main as fhgCD
import matplotlib.dates as mdates

#df = pd.read_csv('combined_simulation_results.csv',sep=',')
df1 = pd.read_excel('data/process_data/Manheim_data_cleaned3.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
df2 = pd.read_csv('full_simulation_results.csv',sep=',')

fhgCD.set_matplotlib_style("scientific", "official")

df1['Column1'] = pd.to_datetime(df1['Column1'])
df2['datetime'] = pd.to_datetime(df2['datetime'])


# Absolute error
error_abs = df2['COP'].values - df1['Column4'].values

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df1['Column1'], error_abs,  label='Absolute Error')

# Monthly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

# Improve readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

ax.set_xlabel('Month')
ax.set_ylabel('Error absolute (COP)')
ax.legend()
ax.set_title('Absolute Error between given and calculated COP')
ax.grid(True)
plt.tight_layout()
plt.show()

# Relative error (in %)
error_rel = (df2['COP'].values - df1['Column4'].values) / df1['Column4'].values * 100

fig,ax =  plt.subplots(figsize=(10, 4))
ax.plot(df1['Column1'], error_rel, label='Relative Error')

# Monthly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

# Improve readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
ax.set_xlabel('Date ime')
ax.set_ylabel('Error relative (COP) %')
ax.set_title('Relative Error between given and calculated COP')
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.show()


# Compare compressor powers
fig,ax =  plt.subplots(figsize=(10, 4))
ax.plot(df1['Column1'], df1['Column22'], label='Compressor Power given')
df2['Compressor Power [kW]'] = df2['Compressor Power [W]']/1e3
ax.plot(df2['datetime'], df2['Compressor Power [kW]'], label='Compressor Power simulated')

# Monthly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

# Improve readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

ax.set_xlabel("Date time")
ax.set_ylabel("Compressor Power in kW")
ax.set_title("Compressor Power given vs calculated in kW")
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.show()
