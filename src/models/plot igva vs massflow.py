'''
Plot frequency of residual of COP, R^2 and standard deviation
'''
import matplotlib.pyplot as plt
import pandas as pd
#import fhgcd_plots.main as fhgCD
import matplotlib.dates as mdates
import numpy as np

df = pd.read_csv('charmap_simulation_results1.csv',sep=',')





fig, ax = plt.subplots(figsize=(8, 4)) 
X_value = df['Speed line X'].round(3).dropna().uniqu
for x in X_value:
    filtered_df = df[df['Speed line X'].round(3) == x]

    x_data = filtered_df['m1'].values
    y_data = filtered_df['igva1'].values
    
    # Scatter
    ax.scatter(x_data, y_data, marker='x',
               label=f'IGVA Compressor 1 for X = {x}')
    
    # ---- Linear Fit ----
    if len(x_data) > 2:  # avoid fitting if too few points
        coeffs = np.polyfit(x_data, y_data, 1)  # degree 1 = linear
        fit_line = np.poly1d(coeffs)
        
        x_sorted = np.sort(x_data)
        ax.plot(x_sorted, fit_line(x_sorted))



ax.set_xlabel('Mass flow (kg/s)')
ax.set_ylabel('Igva (°)')
ax.set_title(f"Effect of mass flow on inlet guide vane angle")
ax.grid(True)
ax.legend()
plt.savefig("igva1.png", dpi=300, bbox_inches="tight")

fig, ax1 = plt.subplots(figsize=(8, 4)) 
x_value = df['Speed line x'].round(3).dropna().unique()
for x in x_value:
    filtered_df = df[df['Speed line x'].round(3) == x]
    X_data = filtered_df['m2'].values
    Y_data = filtered_df['igva2'].values
    
    # Scatter
    ax1.scatter(X_data, Y_data, marker='x',
               label=f'IGVA Compressor 2 for X = {x}')
    
    # ---- Linear Fit ----
    if len(X_data) > 2:  # avoid fitting if too few points
        Coeffs = np.polyfit(X_data, Y_data, 1)  # degree 1 = linear
        Fit_line = np.poly1d(Coeffs)
        
        X_sorted = np.sort(X_data)
        ax1.plot(X_sorted, Fit_line(X_sorted))


ax1.set_xlabel('Mass flow (kg/s)')
ax1.set_ylabel('Igva (°)')
ax1.set_title(f"Effect of mass flow on inlet guide vane angle")
ax1.grid(True)
ax1.legend()
plt.savefig("igva2.png", dpi=300, bbox_inches="tight")

plt.tight_layout()
plt.show()


