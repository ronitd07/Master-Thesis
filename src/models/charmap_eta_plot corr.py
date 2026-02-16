'''
Plot characteristic pr char maps for compressor
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from sklearn.linear_model import HuberRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from scipy.interpolate import UnivariateSpline
#import fhgcd_plots.main as fhgCD

df = pd.read_csv('compressor_results.csv',sep=',')
df0 = pd.read_csv('charmap_simulation_results1.csv',sep=',')
df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
df1_10 = df1['Column6'][::10]

#df['X'].to_excel('X_values.xlsx', index=False, header=['Column1']) 

m1_design = 118.80677445124788
pr1_design = 5.096810782032433
p1_design = 1.9620112316612908 # in bar
e1_design = 0.85

phi = df0['m1']/m1_design
k_raw = df0['eta1'] / e1_design

# Step 1: sort phi and apply same order to k_raw
sort_idx = np.argsort(phi.values)
phi_sorted = phi[sort_idx]
k_sorted = k_raw[sort_idx]

# s = smoothing factor; increase for smoother curve
spline_k = UnivariateSpline(phi_sorted, k_sorted, s=0.001)  

phi_test = np.linspace(min(phi_sorted), max(phi_sorted), 100)
k_smooth = spline_k(phi_test)

plt.scatter(phi, k_raw, label='Raw k')
plt.plot(phi_test, k_smooth, 'r', label='Spline k')
plt.xlabel('Normalized mass flow φ')
plt.ylabel('Correction factor k')
plt.legend()
plt.show()
