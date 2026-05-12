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
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
#import fhgcd_plots.main as fhgCD

df = pd.read_csv('compressor_results1.csv',sep=',')
df0 = pd.read_csv('charmap_simulation_results1.csv',sep=',')
df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
df1_10 = df1['Column6'][::10]

#df['X'].to_excel('X_values.xlsx', index=False, header=['Column1']) 

m1_design = 116.84458779580719
pr1_design = 5.066214041567378
p1_design = 1.9620112316612908 # in bar
e1_design = 0.8


#fhgCD.set_matplotlib_style("scientific", "official")
#fig, ax = plt.subplots(figsize=(10, 4))

x = df['X']
y = (df['Comp1 m'].to_numpy() * p1_design) /(m1_design * df1['Column6'] * x * (1-df['igva1']/100))
z = df['Comp1 eff']/(e1_design * (1 - df['igva1']**2 / 10000))

#y = (df['Comp1 m'].to_numpy() * p1_design) /(m1_design * df1['Column6'] * x )
#z = df['Comp1 eff']/(e1_design)

new_df = pd.DataFrame({
    'x': x,
    'y': y,
    'z': z
})
5
x_val = 0.9589590547888275 

result = new_df[new_df['x'].round(12) == round(x_val,12)]

print(result[['x','y', 'z']])

