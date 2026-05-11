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
import fhgcd_plots.main as fhgCD

df = pd.read_csv('compressor_results1.csv',sep=',')
df0 = pd.read_csv('charmap_simulation_results1.csv',sep=',')
df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
df1_10 = df1['Column6'][::10]

m2_design = 177.78266463515115
pr2_design = 2.8615636254804433
p2_design = 10 # in bar
e2_design = 0.75


fhgCD.set_matplotlib_style("darkgrid", "official")
fig, ax = plt.subplots(figsize=(10, 4))

x = df['Speed line x'].round(4)
y = (df['Comp2 m'].to_numpy() * p2_design) /(m2_design * df1['Column19'] * x * (1-df['igva2']/100))
z = df['Comp2 eff']/(e2_design * (1 - df['igva2']**2 / 10000))
sc = ax.scatter(y, z,
         label='Efficiency compressor 2', c=x, cmap='viridis')

cbar = fig.colorbar(sc,ax=ax)
cbar.set_label('X')  # <- colormap title


ax.set_xlabel('Y')
ax.set_ylabel('Z')
ax.legend()
ax.grid(True)

new_df = pd.DataFrame({
    'x': x,
    'y': y,
    'z': z
})
fig1, ax = plt.subplots(figsize=(10, 4))
x_values_to_plot = [
   0.9902,
   0.9921,
   0.9923,
   1.0023,
   1.0033,
   1.0038,
   1.004,
   1.0043,
   1.0046,
   1.0047
  ]
#x_values_to_plot = np.sort(x.dropna().unique())
#print(x_values_to_plot)

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
    ax.scatter(y_data, z_data, label=f'X = {x_value}')

    # Plot fitted curve
    ax.plot(y_smooth, z_smooth,linewidth=2,linestyle="-")


print(f' "x" : {x_values_to_plot},\n "y" : {y_all},\n "z" :  {z_all}')
plt.title('Efficiency curve fitting for Compressor stage 2')
plt.xlabel('Y')
plt.ylabel('Z')
plt.legend(loc='lower right', bbox_to_anchor=(0.98, 0.02), fontsize=7)
plt.grid(True)
plt.savefig("fit_eta2.png", dpi=300, bbox_inches="tight")

results_df = pd.DataFrame(results, columns=['X','R2','RMSE','MAE','COUNT'])
good_lines = results_df.sort_values(by=['COUNT','R2', 'RMSE'], ascending=[False, False,True])

#filtered = results_df[results_df['COUNT'] > 30]   # choose threshold
#good_lines = filtered.sort_values(by='RMSE')
good_lines.to_csv('eta2_fit.csv', index=False)

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

