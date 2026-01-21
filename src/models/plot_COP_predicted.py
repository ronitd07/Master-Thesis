'''
- Plot with months in the x date time axis and COP cal and simulated in y axis
- Compare compressor powers
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import fhgcd_plots.main as fhgCD

df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
df1_10 = df1.iloc[::10]
#df2 = pd.read_csv('full_simulation_results.csv',sep=',')


#df1 = pd.read_excel('data/process_data/Data 50.xlsx', sheet_name="Tabelle1", header=0,skiprows=range(1, 5)) #Load profile data
df2 = pd.read_csv('power_predictions.csv',sep=',')
df2['COP'] = df1['Column30'][:5]/((df2['Prediction1'] + df2['Prediction2'])/1e3)
df2['Power'] = df2['Prediction1'] + df2['Prediction2']

df3 = pd.read_csv('simulation_results.csv',sep=',')
df3['Power'] = (df3['Compressor Power1 [W]'] + df3['Compressor Power2 [W]'])/1e3  # in kW

df1['Column1'] = pd.to_datetime(df1['Column1'])
df3['datetime'] = pd.to_datetime(df3['datetime'])



#fhgCD.set_matplotlib_style("scientific", "official")
fig1, ax = plt.subplots(figsize=(10, 4))

ax.plot(df1['Column1'][:5], df1['Column4'][:5],
         label='COP given',marker = 'x')
ax.plot(df1['Column1'][:5], df2['COP'],
        label='COP regression',marker = 'x')
ax.plot(df3['datetime'][:5], df3['COP'],
        label='COP simulated',marker = 'x')

# Monthly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

# Improve readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

ax.set_xlabel('Month')
ax.set_ylabel('COP')
ax.legend()
ax.grid(True)

##### Compressor Power compare

fig2, ax = plt.subplots(figsize=(10, 4))

ax.plot(df1['Column1'][:5], df1['Column22'][:5],
         label='Power given (kW)',marker = 'x')
ax.plot(df1['Column1'][:5], df2['Power'],
        label='Power regression (kW)',marker = 'x')
ax.plot(df3['datetime'][:5], df3['Power'],
        label='Power simulated (kW)',marker = 'x')

# Monthly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Jan, Feb, ...

# Improve readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

ax.set_xlabel('Month')
ax.set_ylabel('Compressor Power (kW)')
ax.legend()
ax.grid(True)

plt.show()