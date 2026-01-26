'''
Plot characteristic lines of compressor stages 1,2 
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import fhgcd_plots.main as fhgCD

df = pd.read_csv('compressor_results.csv',sep=',')

m1_design = 118.80677445124788
pr1_design = 5.096810782032433
e1_design = 0.85
m2_design = 191.97196661588126
pr2_design = 3.0593984241028647
e2_design = 0.85


#fhgCD.set_matplotlib_style("scientific", "official")
fig, ax = plt.subplots(figsize=(10, 4))

x = df['Comp1 m']/m1_design
z = df['Comp1 eff']
y = df['pr1']/pr1_design
ax.scatter(x, y,
         label='Pressure ratio',color='tab:blue')

# Right axis: efficiency with colormap
ax2 = ax.twinx()
sc = ax2.scatter(
    x, z,
    c=z,                 # values mapped to colors
    cmap='viridis',      # colormap
    label='Efficiency'
)

# Optional: colorbar for efficiency
cbar = plt.colorbar(sc, ax=ax2)
cbar.set_label('Normalized efficiency')


ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()
ax2.legend()
ax.grid(True)

coeffs2 = np.polyfit(x, y,2)
print("3rd-degree coefficients:", coeffs2)

x_fit = np.linspace(min(x), max(x), 100)

y_fit = np.polyval(coeffs2,x_fit)

ax.scatter(x_fit,y_fit)
ax.set_xlim(0,1.2)

fig1, ax = plt.subplots(figsize=(10, 4))

X = df['Comp2 m']/m2_design
Z = df['Comp2 eff']/e2_design
Y = df['pr2']/pr2_design

ax.scatter(X, Y,
        label='Compressor2 charline')
ax.scatter(X, Z,
        label='Compressor2 charline')

Coeffs2 = np.polyfit(X, Y,2)
print("3rd-degree coefficients:", Coeffs2)

X_fit = np.linspace(min(X), max(X), 100)

Y_fit = np.polyval(Coeffs2,X_fit)

ax.scatter(X_fit,Y_fit)
ax.set_xlim(0,1.2)


ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()
ax.grid(True)

print(x_fit,y_fit,X_fit,Y_fit)

plt.tight_layout()
plt.show()

