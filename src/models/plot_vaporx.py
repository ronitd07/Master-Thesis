'''
Plot with months in the x date time axis and COP cal and simulated in y axis
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import fhgcd_plots.main as fhgCD

df1 = pd.read_excel('data/process_data/Manheim_data_cleaned3.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
df2 = pd.read_csv('simulation_results.csv',sep=',')

df1['Column1'] = pd.to_datetime(df1['Column1'])
df2['datetime'] = pd.to_datetime(df2['datetime'])

fhgCD.set_matplotlib_style("scientific", "official")
fig, ax = plt.subplots(figsize=(10, 4))

ax.plot(df1['Column1'], df1['Column18'],
         label='vapor fraction given')

df2['Ft_x'] = df2['Vapour fraction Flash tank'] * 100; # in %

ax.plot(df2['datetime'], df2['Ft_x'],
        label='vapor fraction cal')

# Monthly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

# Improve readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

ax.set_xlabel('Month')
ax.set_ylabel('COP')
ax.legend()
ax.grid(True)

plt.tight_layout()
plt.show()
