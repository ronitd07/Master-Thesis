import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv('charmap_simulation_results_prmap.csv', sep=',')

# -----------------------------
# Keep only rows where both values exist
# -----------------------------
df_clean = df[['cop_given', 'cop']].dropna().copy()

#To remove outliers of COP < 2.4
#df_clean = df[(df['cop_given'] > 2.4) & (df['cop'].notna())]

y_measured = df_clean['cop_given'].values
y_model = df_clean['cop'].values

# -----------------------------
# Metric functions
# -----------------------------
def rmse(y_measured, y_model):
    return np.sqrt(np.mean((y_model - y_measured) ** 2))

def mape(y_measured, y_model):
    return np.mean(np.abs((y_model - y_measured) / y_measured)) * 100

# -----------------------------
# Compute NMBE Normalized mean bias error
# -----------------------------

def nmbe(y_measured, y_model, p=0):
    y_measured = np.array(y_measured)
    y_model = np.array(y_model)
    n = len(y_measured)
    return np.sum(y_model - y_measured) / ((n - p) * np.mean(y_measured)) * 100

# -----------------------------
# Compute metrics
# -----------------------------
R2 = r2_score(y_measured, y_model)

error_abs = np.abs(y_model - y_measured)
std_error = np.std(error_abs, ddof=1)

rmse_value = rmse(y_measured, y_model)
mape_value = mape(y_measured, y_model)
nmbe_value = nmbe(y_measured, y_model)
print(f"NMBE = {nmbe_value:.2f} %")

print(f"R^2 = {R2:.3f}")
print(f"Standard deviation of absolute error = {std_error:.3f}")
print(f"RMSE = {rmse_value:.3f}")
print(f"MAPE = {mape_value:.2f} %")



# -----------------------------
# Plot simulated COP vs real COP
# -----------------------------
fig, ax = plt.subplots(figsize=(8, 4))

# line of perfect agreement
x_line = np.linspace(min(y_measured.min(), y_model.min()),
                     max(y_measured.max(), y_model.max()), 100)

ax.plot(
    y_measured,
    y_model,
    'o',
    label=(
        f'$R^2$ = {R2:.3f}\n'
        f'RMSE = {rmse_value:.3f}\n'
        f'MAPE = {mape_value:.2f} %\n'
        f'$\\sigma$ = {std_error:.3f}\n'
        f'NMBE= {nmbe_value:.2f} %'
    )
)

ax.plot(x_line, x_line, '-')

ax.set_xlabel('Real COP')
ax.set_ylabel('Simulated COP')
ax.set_title('Comparison of Simulated COP and Real COP')
ax.grid(True)
ax.legend(fontsize=12)

plt.tight_layout()
plt.savefig("COP_compare_metrics.png", dpi=300, bbox_inches="tight")
plt.show()