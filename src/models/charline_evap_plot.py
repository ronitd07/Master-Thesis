'''
Plot characteristic lines of compressor stages 1,2 
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
#import fhgcd_plots.main as fhgCD

df = pd.read_csv('compressor_results_test.csv',sep=',')

# keep only rows where kA is not NaN
df = df[df['kA'].notna()]

kA_design = 2060347.3503932029
m_design = 116.84458779580694



#fhgCD.set_matplotlib_style("scientific", "official")
fig, ax = plt.subplots(figsize=(10, 4))

x = df['Comp1 m']/m_design
y = df['kA']/kA_design
ax.scatter(x, y,
         label='kA evaporator',color='tab:blue')


coeffs2 = np.polyfit(x, y,1)
print("1st-degree coefficients:", coeffs2)

x_fit = np.linspace(min(x), max(x), 10)

y_fit = np.polyval(coeffs2,x_fit)

ax.plot(x_fit,y_fit,color='tab:red',label = 'Fitted 1st degree polynomial')

ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()
ax.grid(True)

plt.savefig("kA_evap_charline.png", dpi=300, bbox_inches="tight")

print(f'x = {x_fit.tolist()}')
print(f'y = {y_fit.tolist()}')

plt.tight_layout()
plt.show()

