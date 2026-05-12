'''
- Plot with months in the x date time axis and COP cal and simulated in y axis
- Compare compressor powers
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
#import fhgcd_plots.main as fhgCD

df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
df1_10 = df1.iloc[::10]
#df2 = pd.read_csv('simulation_results2.csv',sep=',')


#df1 = pd.read_excel('data/process_data/Data 50.xlsx', sheet_name="Tabelle1", header=0,skiprows=range(1, 5)) #Load profile data
df2 = pd.read_csv('charmap_simulation_results6.csv',sep=',')
df3 = pd.read_csv('charline_simulation_results.csv',sep=',')

df1['Column1'] = pd.to_datetime(df1['Column1'])
df2['datetime'] = pd.to_datetime(df2['datetime'])

#fhgCD.set_matplotlib_style("scientific", "official")
fig1, ax = plt.subplots(figsize=(10, 4))

ax.scatter(df2['datetime'], df2['cop_given'],marker = 'x',
         label='COP given')
ax.scatter(df2['datetime'], df2['cop'], marker = 'x',
        label='COP charmap cal')


# Monthly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

# Improve readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

ax.set_xlabel('Month')
ax.set_ylabel('COP')
ax.legend()
ax.grid(True)
plt.savefig("COP compare.png", dpi=300, bbox_inches="tight")

'''
#fhgCD.set_matplotlib_style("scientific", "official")
fig, ax = plt.subplots(figsize=(10, 4))


df2['cp1 [kW]'] = df2['cp1'] / 1e3
df2['cp2 [kW]'] = df2['cp2'] / 1e3
df2['cp [kW]'] = df2['cp1 [kW]'] + df2['cp2 [kW]']

ax.plot(df2['datetime'], df1['Column38'][::10],
        label='Compressor 2 power real' ,marker = 'o')
print(f'Mean cp2 given : {df1['Column38'][::10].mean().round(2)} kW')
ax.plot(df2['datetime'], df2['cp2 [kW]'],
        label='Compressor 2 power simulated' ,marker = 'x')
print(f'Mean cp2 : {df2['cp2 [kW]'].mean().round(2)} kW')

# Monthly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

# Improve readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

ax.set_xlabel('Month')
ax.set_ylabel('Compressor Power [kW]')
ax.legend()
ax.grid(True)
plt.savefig("Compressor2 Power compare.png", dpi=300, bbox_inches="tight")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df2['datetime'], df1['Column37'][::10],
        label='Compressor 1 power real' ,marker = 'o')
print(f'Mean cp1 given : {df1['Column37'][::10].mean().round(2)} kW')

ax.plot(df2['datetime'], df2['cp1 [kW]'],
        label='Compressor 1 power simulated' ,marker = 'x')
print(f'Mean cp1 : {df2['cp1 [kW]'].mean().round(2)} kW')





# Monthly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

# Improve readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

ax.set_xlabel('Month')
ax.set_ylabel('Compressor Power [kW]')
ax.legend()
ax.grid(True)
plt.savefig("Compressor1 Power compare.png", dpi=300, bbox_inches="tight")

fig, ax = plt.subplots(figsize=(10, 4))


ax.plot(df2['datetime'], df2['cp1 [kW]']/df2['cp2 [kW]'] ,label='Compressor Power ratio')




# Monthly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

# Improve readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

ax.set_xlabel('Month')
ax.set_ylabel('Compressor Power ratio [-]')
ax.legend()
ax.grid(True)
plt.savefig("Compressor Power ratio.png", dpi=300, bbox_inches="tight")
'''
plt.tight_layout()
plt.show()
