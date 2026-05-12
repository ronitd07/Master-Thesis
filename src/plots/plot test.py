'''
- Plot with months in the x date time axis and COP cal and simulated in y axis
- Compare compressor powers
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
#import fhgcd_plots.main as fhgCD

df = pd.read_csv('charmap_simulation_results3.csv',sep=',')
df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
df2 = pd.read_csv('compressor_results1.csv',sep=',')


df['datetime'] = pd.to_datetime(df['datetime'])
df2['datetime'] = pd.to_datetime(df2['datetime'])

fig, ax = plt.subplots(figsize=(10, 4))

ax.scatter(df2['datetime'][::10],df2['Comp1 eff'][::10] ,marker = 'o',
         label='Compressor 1 efficiency real')
ax.scatter(df['datetime'],df['eta1'] ,marker = 'x',
         label='Compressor 1 efficiency simulated')
print(f'Evaporator pressure mean given : {df1['Column6'][::10].mean()}, simulated {df['Evaporator pressure'].mean()}')



# Monthly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

# Improve readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

ax.set_xlabel('Month')
ax.set_ylabel('Efficiency Compressor 1')
ax.legend()
ax.grid(True)
plt.savefig("Eff compressor1.png", dpi=300, bbox_inches="tight")

fig, ax1 = plt.subplots(figsize=(10, 4))

ax1.scatter(df2['datetime'][::10],df2['Comp2 eff'][::10] ,marker = 'o',
         label='Compressor 2 efficiency real')
ax1.scatter(df['datetime'],df['eta2'] ,marker = 'x',
         label='Compressor 2 efficiency simulated')




# Monthly ticks
ax1.xaxis.set_major_locator(mdates.MonthLocator())
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

# Improve readability
plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')

ax1.set_xlabel('Month')
ax1.set_ylabel('Efficiency Compressor 2')
ax1.legend()
ax1.grid(True)
plt.savefig("Eff compressor2.png", dpi=300, bbox_inches="tight")

plt.tight_layout()
plt.show()
