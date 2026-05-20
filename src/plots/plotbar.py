'''
Plot frequency of residual of COP
'''
import matplotlib.pyplot as plt
import pandas as pd
import fhgcd_plots.main as fhgCD
import matplotlib.dates as mdates
import numpy as np


# -----------------------------
# Load data
# -----------------------------
while True:
    choice = input("Which result file do you want to run? Enter 'charline' or 'charmap' or 'compressor': ").strip().lower()


    if choice == "charline":
        file_name = "charline_simulation_results.csv"
        break
    elif choice == "charmap":
        file_name = "charmap_simulation_results.csv"
        break
    elif choice == "compressor":
        file_name = "compressor_simulation_results.csv"
        break    
    else:
        print("Invalid choice. Please enter either 'charline' or 'charmap' or 'compressor'.")

df = pd.read_csv(file_name, sep=",")

fhgCD.set_matplotlib_style("darkgrid", "official")

# Absolute error
error_abs = df['cop'].values - df['cop_given'].values


fig, ax = plt.subplots(figsize=(8, 4))

ax.hist(error_abs, bins='fd',rwidth=0.8,label='Frequency')

ax.set_xlabel('Residual (COP)')
ax.set_ylabel('Frequency')
#ax.set_title('Frequency distribution of residuals of COP')
ax.grid(True, axis="y", alpha=0.3, zorder=0)
ax.legend()
ax.set_xlim(-0.5,0.5)
plt.savefig("COP residual barplot.png", dpi=300, bbox_inches="tight")
plt.tight_layout()
plt.show()


