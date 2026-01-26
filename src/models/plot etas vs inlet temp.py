'''
- Plot eta_s vs pr of compressor 1 and 2
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import fhgcd_plots.main as fhgCD
import numpy as np


df = pd.read_csv('sensitivity_simulation_results.csv',sep=',')


#fhgCD.set_matplotlib_style("scientific", "official")
fig, ax = plt.subplots(figsize=(10, 4))

ax.scatter(df['Temp in cp1'], df['Efficiency comp1'],
         label='Efficiency vs inlet temperature at Compressor 1')


ax.set_xlabel('Inlet temperature to compressor 1 (°C)')
ax.set_ylabel('efficiency comp1')
ax.legend()
ax.grid(True)

coeffs2 = np.polyfit(df['Temp in cp1'], df['Efficiency comp1'],2)
print("2nd-degree coefficients:", coeffs2)
x_fit = np.linspace(min(df['Temp in cp1']), max(df['Temp in cp1']), 100)
y_fit = np.polyval(coeffs2,x_fit)

ax.scatter(x_fit,y_fit,label = '2nd degree polynomial fit' )
ax.legend()
#ax.set_xlim(0,1.2)


#compressor 2
fig1, ax = plt.subplots(figsize=(10, 4))

ax.scatter(df['Temp in cp2'], df['Efficiency comp2'],
         label='Efficiency vs inlet temperature at Compressor 2')


ax.set_xlabel('Inlet temperature to compressor 2 (°C)')
ax.set_ylabel('efficiency comp2')
ax.legend()
ax.grid(True)


Coeffs2 = np.polyfit(df['Temp in cp2'], df['Efficiency comp2'],2)
print("2nd-degree coefficients:", Coeffs2)
X_fit = np.linspace(min(df['Temp in cp2']), max(df['Temp in cp2']), 100)
Y_fit = np.polyval(Coeffs2,X_fit)

ax.scatter(X_fit,Y_fit,label = '2nd degree polynomial fit' )
ax.legend()



plt.tight_layout()
plt.show()
