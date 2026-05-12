import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import fhgcd_plots.main as fhgCD

# Load data
df2 = pd.read_csv(r'results/charmap_simulation_results6.csv', sep=',')


# --- Clean and align data properly ---
df = df2[['Speed line X', 'cop', 'cop_given','Comp1 eff','Comp2 eff']].dropna().copy()
df[['Comp1 eff', 'Comp2 eff']] = df[['Comp1 eff', 'Comp2 eff']].round(2)

# --- Compute absolute error ---
df['error_abs'] = np.abs(df['cop'] - df['cop_given'])


# --- Group data ---
grouped = df.groupby('Comp1 eff')['error_abs']

# --- Prepare boxplot data ---
data = [group for _, group in grouped]
labels = [str(name) for name, _ in grouped]

# --- Plot ---
#fhgCD.set_matplotlib_style("grid", "official")
fig, ax = plt.subplots(figsize=(10, 5))

ax.boxplot(data, tick_labels=labels)

ax.set_xlabel('Compressor 1 isentropic efficiency')
ax.set_ylabel('COP Absolute Error')
ax.set_title('COP Error Distribution per isentropic efficiency for Compressor 1')
ax.grid(True)

plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("COP_boxplot_speedline_compressor1.png", dpi=300, bbox_inches="tight")
plt.show()

# -------------------------
# Count per speedline
# -------------------------
count_per_speedline = df.groupby('Comp1 eff').size()

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(count_per_speedline.index.astype(str), count_per_speedline.values)

ax.set_xlabel('Compressor 1 efficiency')
ax.set_ylabel('Number of Data Points')
ax.set_title('Number of Data Points per efficiency for Compressor 1')
ax.grid(True, axis='y')

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("COP_count_per_speedline_compressor1.png", dpi=300, bbox_inches="tight")
plt.show()