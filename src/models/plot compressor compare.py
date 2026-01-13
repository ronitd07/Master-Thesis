'''
compressor compare for first 50 data items
'''
import matplotlib.pyplot as plt
import pandas as pd
import fhgcd_plots.main as fhgCD
import matplotlib.dates as mdates

#df = pd.read_csv('combined_simulation_results.csv',sep=',')
df1 = pd.read_excel('data/process_data/Data 50.xlsx', sheet_name="Tabelle1", header=0,skiprows=range(1, 5)) #Load profile data
df2 = pd.read_csv('simulation_results.csv',sep=',')

fhgCD.set_matplotlib_style("scientific", "official")

df1['Column1'] = pd.to_datetime(df1['Column1'])
df2['datetime'] = pd.to_datetime(df2['datetime'])

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