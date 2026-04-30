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

x = df['Speed line X'].round(4)
y = (df['Comp1 m'].to_numpy() * p1_design) /(m1_design * df1['Column6'] * x * (1-df['igva1']/100))
z = df['Comp1 eff']/(e1_design * (1 - df['igva1']**2 / 10000))

#y = (df['Comp1 m'].to_numpy() * p1_design) /(m1_design * df1['Column6'] * x )
#z = df['Comp1 eff']/(e1_design)

new_df = pd.DataFrame({
    'x': x,
    'y': y,
    'z': z
})

fig1, ax = plt.subplots(figsize=(10, 4))
x_values_to_plot = np.sort(x.unique())
#x_values_to_plot = [val for val in x_values_to_plot if 0.98 < val < 0.9999]
x_values_to_plot = [0.9913,0.9914
  ]

x_all = []
y_all = []
z_all = []
results = []

for x_value in x_values_to_plot:
    filtered_df = new_df[new_df['x'] == x_value]

    y_data = filtered_df['y'].to_numpy()
    z_data = filtered_df['z'].to_numpy()
    print(f'{x_value} : count {len(y_data)}')
    print(f'{x_value}, y_min {np.min(y_data)}, y_max {np.max(y_data)}')
    y_count = len(y_data)
    # Reshape for sklearn
    Y = y_data.reshape(-1, 1)

    # Huber regression with quadratic features
    model = make_pipeline(
        PolynomialFeatures(degree=2, include_bias=True),
        HuberRegressor(epsilon=1.35, alpha=0.0)
    )

    model.fit(Y, z_data)

    # Smooth curve
    y_smooth = np.linspace(y_data.min(), y_data.max(), 10)
    Y_smooth = y_smooth.reshape(-1, 1)
    z_smooth = model.predict(Y_smooth)

    z_pred = model.predict(Y)

    r2 = r2_score(z_data, z_pred)
    rmse = np.sqrt(mean_squared_error(z_data, z_pred))
    mae = mean_absolute_error(z_data, z_pred)

    results.append([x_value, r2, rmse, mae,y_count])

    # Store values
    y_all.append(y_smooth.tolist())
    z_all.append(z_smooth.tolist())
    

    # Plot scatter points
    ax.scatter(y_data, z_data, label=f'X = {x_value}', alpha=0.5)

    # Plot fitted curve
    ax.plot(y_smooth, z_smooth, linewidth=2,
            label=f'r2 = {round(r2,2)}, rmse =  {round(rmse,2)},count = {len(y_data)} ')

print(f' "x" : {x_values_to_plot},\n "y": {y_all},\n "z" :  {z_all}')

results_df = pd.DataFrame(results, columns=['X','R2','RMSE','MAE','COUNT'])
good_lines = results_df.sort_values(by=['COUNT','R2', 'RMSE'], ascending=[False, False,True])

#filtered = results_df[results_df['COUNT'] > 30]   # choose threshold
#good_lines = filtered.sort_values(by='RMSE')
good_lines.to_csv('eta1_fit.csv', index=False)


plt.title('Efficiency curve fitting for Compressor stage 1')
plt.xlabel('Y')
plt.ylabel('Z')
plt.legend(loc='lower right', bbox_to_anchor=(0.98, 0.02), fontsize=7)
plt.grid(True)
plt.savefig("fit_eta1.png", dpi=300, bbox_inches="tight")
plt.show()
'''

coeffs2 = np.polyfit(x, y,2)
print("2nd-degree coefficients:", coeffs2)

x_fit = np.linspace(min(x), max(x), 10)

y_fit = np.polyval(coeffs2,x_fit)

ax.scatter(x_fit,y_fit,color ='red')
ax.set_xlim(0,1.2)
print(x_fit,y_fit)

# Compressor stage 2
fig1, ax = plt.subplots(figsize=(10, 4))

X = df['Comp2 m']/m2_design
Y = df1['Column42']/pr2_design # pr2 given from data
ax.scatter(X, Y,
         label='Pressure ratio compressor 2',color='tab:blue')


ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()
ax.grid(True)

Coeffs2 = np.polyfit(X, Y,2)
print("2nd-degree coefficients:", Coeffs2)

X_fit = np.linspace(min(X), max(X), 100)

Y_fit = np.polyval(Coeffs2,X_fit)

ax.scatter(X_fit,Y_fit,color ='red')
ax.set_xlim(0,1.2)
print(X_fit,Y_fit)
'''

