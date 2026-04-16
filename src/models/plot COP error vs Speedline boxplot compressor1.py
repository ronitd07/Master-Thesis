import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Load data
df2 = pd.read_csv('charmap_simulation_results1.csv', sep=',')

# --- Clean and align data properly ---
df = df2[['Speed line X', 'cop', 'cop_given']].dropna().copy()

# --- Compute absolute error ---
df['error_abs'] = np.abs(df['cop'] - df['cop_given'])

# --- Round speedline to 3 decimal places ---
df['Speed line X rounded'] = df['Speed line X'].round(3)

# --- Group data ---
grouped = df.groupby('Speed line X rounded')['error_abs']

# --- Prepare boxplot data ---
data = [group for _, group in grouped]
labels = [str(name) for name, _ in grouped]

# --- Plot ---
fig, ax = plt.subplots(figsize=(10, 5))

ax.boxplot(data, tick_labels=labels)

ax.set_xlabel('Speed line X (rounded to 3 decimals)')
ax.set_ylabel('COP Absolute Error')
ax.set_title('COP Error Distribution per Speedline for Compressor 1')
ax.grid(True)

plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("COP_boxplot_speedline_compressor1.png", dpi=300, bbox_inches="tight")
plt.show()

# -------------------------
# Count per speedline
# -------------------------
count_per_speedline = df.groupby('Speed line X rounded').size()

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(count_per_speedline.index.astype(str), count_per_speedline.values)

ax.set_xlabel('Speed line X (rounded to 3 decimals)')
ax.set_ylabel('Number of Data Points')
ax.set_title('Number of Data Points per Speedline for Compressor 1')
ax.grid(True, axis='y')

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("COP_count_per_speedline_compressor1.png", dpi=300, bbox_inches="tight")
plt.show()