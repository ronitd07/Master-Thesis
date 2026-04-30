import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler,PolynomialFeatures
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
import numpy as np

# Load your data
df = pd.read_csv('sensitivity_simulation_results.csv',sep=',')

# Stage 1
x1 = df[['Temp in cp1','Pressure in cp1','Mass flow comp1','pr comp1']]
y1 = df['Efficiency comp1'].values

# Polynomial regression pipeline
poly_model = Pipeline([
    ('scaler', StandardScaler()),
    ('poly', PolynomialFeatures(degree=2, include_bias=False)),
    ('reg', LinearRegression())
])


poly_model.fit(x1, y1)

# Extract coefficients
feature_names = poly_model.named_steps['poly'].get_feature_names_out(x1.columns)
coeffs = poly_model.named_steps['reg'].coef_


# Display sensitivities
for name, coef in zip(feature_names, coeffs):
    print(f"{name}: {coef:.4f}")

fig, ax = plt.subplots(figsize=(8, 4))

short_names = {
    'Temp in cp1': r'$T_{in}$',
    'Pressure in cp1': r'$p_{in}$',
    'Mass flow comp1': r'$\dot{m}$',
    'pr comp1': r'$\pi$',
    'Temp in cp1^2': r'$T_{in}^2$',
    'Pressure in cp1^2': r'$p_{in}^2$',
    'Mass flow comp1^2': r'$\dot{m}^2$',
    'pr comp1^2': r'$\pi^2$',
    'Temp in cp1 Pressure in cp1': r'$T_{in}p_{in}$',
    'Temp in cp1 Mass flow comp1': r'$T_{in}\dot{m}$',
    'Temp in cp1 pr comp1': r'$T_{in}\pi$',
    'Pressure in cp1 Mass flow comp1': r'$p_{in}\dot{m}$',
    'Pressure in cp1 pr comp1': r'$p_{in}\pi$',
    'Mass flow comp1 pr comp1': r'$\dot{m}\pi$'
}

plot_labels = [short_names.get(name, name) for name in feature_names]

x = np.arange(len(feature_names))
ax.bar(x, coeffs)

ax.set_xticks(x)
ax.set_xticklabels(plot_labels, rotation=20)

ax.set_xlabel('Input parameters')
ax.set_ylabel('Polynomial regression coefficient')
ax.set_title('Polynomial Regression-based sensitivity of stage 1 compressor efficiency')

ax.axhline(0, linewidth=0.8)
ax.grid(True, axis='y')

plt.tight_layout()
plt.savefig("Sensitivity poly regression compressor 1", dpi=300, bbox_inches="tight")
plt.show()

# Stage 2
x2 = df[['Temp in cp2','Pressure in cp2','Mass flow comp2','pr comp2']]
y2 = df['Efficiency comp2'].values

# Polynomial regression pipeline
poly_model2 = Pipeline([
    ('scaler', StandardScaler()),
    ('poly', PolynomialFeatures(degree=2, include_bias=False)),
    ('reg', LinearRegression())
])


poly_model2.fit(x2, y2)

# Extract coefficients
feature_names2 = poly_model2.named_steps['poly'].get_feature_names_out(x2.columns)
coeffs2 = poly_model2.named_steps['reg'].coef_


# Display sensitivities
for name, coef in zip(feature_names2, coeffs2):
    print(f"{name}: {coef:.4f}")

fig1, ax = plt.subplots(figsize=(8, 4))

short_names2 = {
    'Temp in cp2': r'$T_{in}$',
    'Pressure in cp2': r'$p_{in}$',
    'Mass flow comp2': r'$\dot{m}$',
    'pr comp2': r'$\pi$',
    'Temp in cp2^2': r'$T_{in}^2$',
    'Pressure in cp2^2': r'$p_{in}^2$',
    'Mass flow comp2^2': r'$\dot{m}^2$',
    'pr comp2^2': r'$\pi^2$',
    'Temp in cp2 Pressure in cp2': r'$T_{in}p_{in}$',
    'Temp in cp2 Mass flow comp2': r'$T_{in}\dot{m}$',
    'Temp in cp2 pr comp2': r'$T_{in}\pi$',
    'Pressure in cp2 Mass flow comp2': r'$p_{in}\dot{m}$',
    'Pressure in cp2 pr comp2': r'$p_{in}\pi$',
    'Mass flow comp2 pr comp2': r'$\dot{m}\pi$'
}

plot_labels2 = [short_names2.get(name, name) for name in feature_names2]

x = np.arange(len(feature_names2))
ax.bar(x, coeffs2)

ax.set_xticks(x)
ax.set_xticklabels(plot_labels2, rotation=20)

ax.set_xlabel('Input parameters')
ax.set_ylabel('Polynomial regression coefficient')
ax.set_title('Polynomial Regression-based sensitivity of stage 2 compressor efficiency')

ax.axhline(0, linewidth=0.8)
ax.grid(True, axis='y')

plt.tight_layout()
plt.savefig("Sensitivity poly regression compressor 2", dpi=300, bbox_inches="tight")
plt.show()
