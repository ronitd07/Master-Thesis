'''
Plot characteristic pr char maps for compressor
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from sklearn.linear_model import HuberRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
#import fhgcd_plots.main as fhgCD

df = pd.read_csv('compressor_results.csv',sep=',')
df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data

#df['X'].to_excel('X_values.xlsx', index=False, header=['Column1']) 

m1_design = 118.80677445124788
pr1_design = 5.096810782032433
p1_design = 1.9620112316612908 # in bar
e1_design = 0.85


#fhgCD.set_matplotlib_style("scientific", "official")
fig, ax = plt.subplots(figsize=(10, 4))

x = df['X'].round(3)
y = df['Comp1 m'] * p1_design /(m1_design * df1['Column6'] * x)
z = df['Comp1 eff']/e1_design # pr1 given from data
sc = ax.scatter(y, z,
         label='Efficiency compressor 1', c=x, cmap='viridis')

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
x_values_to_plot = x.unique()
#x_values_to_plot = [0.971, 0.98]

for x_value in x_values_to_plot:
    filtered_df = new_df[new_df['x'] == x_value]

    x_data = filtered_df['y'].to_numpy()
    y_data = filtered_df['z'].to_numpy()

    # Reshape for sklearn
    X = x_data.reshape(-1, 1)

    # Huber regression with quadratic features
    model = make_pipeline(
        PolynomialFeatures(degree=2, include_bias=True),
        HuberRegressor(epsilon=1.35, alpha=0.0)
    )

    model.fit(X, y_data)

    # Smooth curve
    x_smooth = np.linspace(x_data.min(), x_data.max(), 200)
    X_smooth = x_smooth.reshape(-1, 1)
    y_smooth = model.predict(X_smooth)

    print(x_value, x_smooth[::40], y_smooth[::40])

    # Plot scatter points
    ax.scatter(x_data, y_data, label=f'X = {x_value}', alpha=0.5)

    # Plot fitted curve
    ax.plot(x_smooth, y_smooth, linewidth=2,
            label=f'Huber fit X = {x_value}')

plt.title('Efficiency curve fitting for Compressor stage 1')
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

