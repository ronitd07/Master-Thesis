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

x = np.arange(len(feature_names))
ax.bar(x, coeffs)

ax.set_xticks(x)
ax.set_xticklabels(feature_names, rotation=20)

ax.set_xlabel('Input parameters')
ax.set_ylabel('Polynomial regression coefficient')
ax.set_title('Polynomial Regression-based sensitivity of stage 1 compressor efficiency')

ax.axhline(0, linewidth=0.8)
ax.grid(True, axis='y')

plt.tight_layout()
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

x = np.arange(len(feature_names2))
ax.bar(x, coeffs2)

ax.set_xticks(x)
ax.set_xticklabels(feature_names2, rotation=20)

ax.set_xlabel('Input parameters')
ax.set_ylabel('Polynomial regression coefficient')
ax.set_title('Polynomial Regression-based sensitivity of stage 2 compressor efficiency')

ax.axhline(0, linewidth=0.8)
ax.grid(True, axis='y')

plt.tight_layout()
plt.show()
