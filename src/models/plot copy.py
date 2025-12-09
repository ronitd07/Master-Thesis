import matplotlib.pyplot as plt
import pandas as pd

#df = pd.read_csv('combined_simulation_results.csv',sep=',')
df1 = pd.read_excel('data/process_data/Manheim_data_cleaned3.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
df2 = pd.read_csv('combined_simulation_results.csv',sep=',')

fig, ax1 = plt.subplots()
# Plot first dataframe (left y-axis)
ax1.plot(df1['Column1'], df1['Column30'], color='blue', label='Q load given')
ax1.set_xlabel("Date time")
ax1.set_ylabel("COP_given", color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# Second y-axis
#ax2 = ax1.twinx()
df2['Q_load MW'] = df2['Q_load [W]'] / 1e6
ax1.plot(df2['datetime'], df2['Q_load MW'], color='red', label='Q load calculated')
#ax2.set_ylabel("COP_cal", color='red')
#ax2.tick_params(axis='y', labelcolor='red')

plt.title("COP calculated vs COP given Over Time")
ax1.legend()
plt.show()

'''
#COP over the year
plt.plot( df["Column1"],df["Column4"], marker='o', color='purple')
plt.title('COP vs Time')
plt.xlabel('Date')
plt.ylabel('COP')
plt.grid(True)

# Adjust layout
plt.tight_layout()
plt.show()
'''
