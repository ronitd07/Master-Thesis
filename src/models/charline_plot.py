'''
Plot characteristic lines of compressor stages 1,2 
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import fhgcd_plots.main as fhgCD

df = pd.read_csv('charline_simulation_results.csv',sep=',')

m1_design = 118.80677445124788
pr1_design = 5.096810782032433
e1_design = 0.85
m2_design = 191.97196661588126
pr2_design = 3.0593984241028647
e2_design = 0.85


#fhgCD.set_matplotlib_style("scientific", "official")
fig, ax = plt.subplots(figsize=(10, 4))

x = df['Mass flow comp1']/m1_design
y = df['Efficiency comp1']/e1_design
ax.scatter(x, y,
         label='eta_s_char compressor 1',color='tab:blue')


coeffs2 = np.polyfit(x, y,2)
print("2nd-degree coefficients:", coeffs2)

x_fit = np.linspace(min(x), max(x), 10)

y_fit = np.polyval(coeffs2,x_fit)

ax.plot(x_fit,y_fit,color='tab:red',label = 'Fitted 2nd degree polynomial')
#ax.set_xlim(0,1.2)

ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()
ax.grid(True)

plt.savefig("eta_charline2 comp1.png", dpi=300, bbox_inches="tight")
fig1, ax = plt.subplots(figsize=(10, 4))

X = df['Mass flow comp2']/m2_design
Y = df['Efficiency comp2']/e2_design

ax.scatter(X, Y,
        label='eta_s_char compressor 2',color='tab:blue')

Coeffs2 = np.polyfit(X, Y,2)
print("2nd-degree coefficients:", Coeffs2)

X_fit = np.linspace(min(X), max(X), 10)

Y_fit = np.polyval(Coeffs2,X_fit)

ax.plot(X_fit,Y_fit,color='tab:red',label = 'Fitted 2nd degree polynomial')
#ax.set_xlim(0,1.2)


ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()
ax.grid(True)
plt.savefig("eta_charline2 comp2.png", dpi=300, bbox_inches="tight")

print(x_fit,y_fit,X_fit,Y_fit)

plt.tight_layout()
plt.show()

