'''
compare compressor 1 and 2 powers after using custom charline
'''
import matplotlib.pyplot as plt
import pandas as pd
import fhgcd_plots.main as fhgCD
import matplotlib.dates as mdates

#df = pd.read_csv('combined_simulation_results.csv',sep=',')
df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
df2 = pd.read_csv('simulation_results.csv',sep=',')

#fhgCD.set_matplotlib_style("scientific", "official")

df1['Column1'] = pd.to_datetime(df1['Column1'])
df2['datetime'] = pd.to_datetime(df2['datetime'])

# Compare compressor powers
fig,ax =  plt.subplots(figsize=(10, 4))
df2['Compressor1 Power [kW]'] = df2['Compressor Power1 [W]']/1e3
ax.plot(df2['datetime'], df2['Compressor1 Power [kW]'], label='Compressor Power1 simulated')
df2['Compressor2 Power [kW]'] = df2['Compressor Power2 [W]']/1e3
ax.plot(df2['datetime'], df2['Compressor2 Power [kW]'], label='Compressor Power2 simulated')


# Monthly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

ax.set_xlabel("Date time")
ax.set_ylabel("Compressor Power in kW")
ax.set_title("Compressor Power given vs calculated in kW")
ax.legend()
ax.grid(True)

#Plot ratio of comp1 and comp2 power
fig1,ax =  plt.subplots(figsize=(10, 4))
ax.plot(df2['datetime'], df2['Compressor1 Power [kW]'] / df2['Compressor2 Power [kW]'], label='Comp1 Power / Comp2 Power')

ax.set_xlabel("Date time")
ax.set_ylabel("Comp1 Power / Comp2 Power ratio")
ax.set_title("Ratio of Compressor1 and Compressor2 Power")
ax.legend()
ax.grid(True)

# Monthly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

# Improve readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.show()