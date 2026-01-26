'''
Plot characteristic pr char maps for compressor
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import fhgcd_plots.main as fhgCD

df = pd.read_csv('compressor_results.csv',sep=',')
df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data

m1_design = 118.80677445124788
pr1_design = 5.096810782032433
e1_design = 0.85
m2_design = 191.97196661588126
pr2_design = 3.0593984241028647
e2_design = 0.85


#fhgCD.set_matplotlib_style("scientific", "official")
fig, ax = plt.subplots(figsize=(10, 4))

x = df['Comp1 m']/m1_design
y = df1['Column41']/pr1_design # pr1 given from data
ax.scatter(x, y,
         label='Pressure ratio compressor 1',color='tab:blue')


ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()
ax.grid(True)

coeffs2 = np.polyfit(x, y,2)
print("2nd-degree coefficients:", coeffs2)

x_fit = np.linspace(min(x), max(x), 10)

y_fit = np.polyval(coeffs2,x_fit)

ax.scatter(x_fit,y_fit,color ='red')
ax.set_xlim(0,1.2)
print(x_fit,y_fit)

# Compressor stage 2
fig1, ax = plt.subplots(figsize=(10, 4))

X = df['Comp2 m']/m2_design
Y = df1['Column42']/pr2_design # pr2 given from data
ax.scatter(X, Y,
         label='Pressure ratio compressor 2',color='tab:blue')


ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()
ax.grid(True)

Coeffs2 = np.polyfit(X, Y,2)
print("2nd-degree coefficients:", Coeffs2)

X_fit = np.linspace(min(X), max(X), 100)

Y_fit = np.polyval(Coeffs2,X_fit)

ax.scatter(X_fit,Y_fit,color ='red')
ax.set_xlim(0,1.2)
print(X_fit,Y_fit)


plt.tight_layout()
plt.show()

