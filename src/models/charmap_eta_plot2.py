'''
Plot characteristic pr char maps for compressor
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
#import fhgcd_plots.main as fhgCD

df = pd.read_csv('compressor_results1.csv',sep=',')
df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data

m2_design = 191.97196661588126
pr2_design = 3.0593984241028647
p2_design = 10 # in bar
e2_design = 0.85


#fhgCD.set_matplotlib_style("scientific", "official")
fig, ax = plt.subplots(figsize=(10, 4))

x = df['x'].round(2)
y = df['Comp2 m'] * p2_design /(m2_design * df1['Column19'] * x)
z = df['Comp2 eff']/e2_design 
sc = ax.scatter(y, z,
         label='Efficiency compressor 2', c=x, cmap='viridis')

cbar = fig.colorbar(sc,ax=ax)
cbar.set_label('X')  # <- colormap title


ax.set_xlabel('Y')
ax.set_ylabel('Z')
ax.legend()
ax.grid(True)

new_df = pd.DataFrame({
    'x': x,
    'y': y,
    'z': z
})
fig1, ax = plt.subplots(figsize=(10, 4))
#x_values_to_plot = (0.96, 0.97, 0.98, 0.99)
x_values_to_plot = x.unique()
for x_value in x_values_to_plot:
    filtered_df = new_df[new_df['x'] == x_value]

    x_data = filtered_df['y'].to_numpy()
    y_data = filtered_df['z'].to_numpy()

    # Fit a 2nd-degree polynomial
    coeffs = np.polyfit(x_data, y_data, deg=2)
    poly = np.poly1d(coeffs)

    # Generate smooth points for the curve
    x_smooth = np.linspace(x_data.min(), x_data.max(), 10)
    y_smooth = poly(x_smooth)
    print(x_value,x_smooth, y_smooth )

    
    # Plot scatter points
    ax.scatter(x_data, y_data, label=f'X = {x_value}')

    # Plot fitted curve
    ax.plot(x_smooth, y_smooth, label=f'Fit X = {x_value}')
    plt.title('Efficiency curve fitting for Compressor stage 2')
    plt.xlabel('Y')
    plt.ylabel('Z')
    plt.legend()
    plt.grid(True)

plt.show()
'''

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
'''

