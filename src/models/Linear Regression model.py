'''
Perform sensitivity analysis of compressor isentropic efficiency using Linear Regression method
'''
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import numpy as np
import fhgcd_plots.main as fhgCD

# Load your data
df = pd.read_csv('sensitivity_simulation_results.csv',sep=',')

# Stage 1
x1 = df[['Temp in cp1','Pressure in cp1','Mass flow comp1','pr comp1']]
y1 = df['Efficiency comp1'].values

# Standardize parameters (important for comparing coefficients)
scaler1 = StandardScaler()
x1_scaled = scaler1.fit_transform(x1)

model1 = LinearRegression()
model1.fit(x1_scaled, y1)

# Coefficients show sensitivity
coeffs1 = model1.coef_
for name, c in zip(['Temp in cp1','Pressure in cp1','Mass flow comp1','pr comp1'], coeffs1):
    print(f"{name}: {c:.3f}")

param_names = ['Temp in cp1',
               'Pressure in cp1',
               'Mass flow comp1',
               'pr comp1']

fhgCD.set_matplotlib_style("grid", "official")
fig, ax = plt.subplots(figsize=(8, 4))

x = np.arange(len(param_names))
ax.bar(x, coeffs1)

ax.set_xticks(x)
ax.set_xticklabels(param_names, rotation=20)

ax.set_ylabel('Standardized regression coefficient')
ax.set_title('Regression-based sensitivity of stage 1 compressor efficiency')

ax.axhline(0, linewidth=0.8)
ax.grid(True, axis='y')

plt.tight_layout()
plt.savefig("Sensitivity linear regression compressor 1_fhgcd", dpi=300, bbox_inches="tight")
plt.show()

# Stage 2
x2 = df[['Temp in cp2','Pressure in cp2','Mass flow comp2','pr comp2']]
y2 = df['Efficiency comp2'].values

# Standardize parameters (important for comparing coefficients)
scaler2 = StandardScaler()
x2_scaled = scaler2.fit_transform(x2)

model2 = LinearRegression()
model2.fit(x2_scaled, y2)

# Coefficients show sensitivity
coeffs2 = model2.coef_
for name, c in zip(['Temp in cp2','Pressure in cp2','Mass flow comp2','pr comp2'], coeffs2):
    print(f"{name}: {c:.3f}")

param_names = ['Temp in cp2',
               'Pressure in cp2',
               'Mass flow comp2',
               'pr comp2']

fig1, ax = plt.subplots(figsize=(8, 4))

x = np.arange(len(param_names))
ax.bar(x, coeffs2)

ax.set_xticks(x)
ax.set_xticklabels(param_names, rotation=20)

ax.set_ylabel('Standardized regression coefficient')
ax.set_title('Regression-based sensitivity of stage 2 compressor efficiency')

ax.axhline(0, linewidth=0.8)
ax.grid(True, axis='y')

plt.tight_layout()
plt.savefig("Sensitivity linear regression compressor 2_fhgcd", dpi=300, bbox_inches="tight")
plt.show()