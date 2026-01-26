'''
Plot characteristic lines of compressor stages 1,2 
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import fhgcd_plots.main as fhgCD
from scipy.interpolate import griddata

df = pd.read_csv('compressor_results.csv',sep=',')

m1_design = 118.80677445124788
pr1_design = 5.096810782032433
e1_design = 0.85
m2_design = 191.97196661588126
pr2_design = 3.0593984241028647
e2_design = 0.85


# Original data
x = df['Comp1 m'] / m1_design
y = df['pr1'] / pr1_design
z = df['Comp1 eff'] / e1_design   # or absolute efficiency

# Create grid
xi = np.linspace(x.min(), x.max(), 200)
yi = np.linspace(y.min(), y.max(), 200)
Xi, Yi = np.meshgrid(xi, yi)

# Interpolate efficiency
Zi = griddata(
    points=(x, y),
    values=z,
    xi=(Xi, Yi),
    method='cubic'   # 'linear' if data is sparse
)

fig, ax = plt.subplots(figsize=(8, 6))

# Filled efficiency islands
contourf = ax.contourf(
    Xi, Yi, Zi,
    levels=15,
    cmap='YlOrRd'
)

# Efficiency contour lines
contour = ax.contour(
    Xi, Yi, Zi,
    levels=10,
    colors='black',
    linewidths=0.8
)

ax.clabel(contour, fmt='%.0f%%', inline=True, fontsize=8)

# Original data points (optional)
#ax.scatter(x, y, c='k', s=10, alpha=0.4)

# Colorbar
cbar = plt.colorbar(contourf, ax=ax)
cbar.set_label('Normalized isentropic efficiency')

ax.set_xlabel(r'$\dot m / \dot m_\mathrm{design}$')
ax.set_ylabel(r'$\pi = p_\mathrm{out}/p_\mathrm{in}$')
ax.set_title('Compressor efficiency map')

ax.grid(True)
plt.show()

