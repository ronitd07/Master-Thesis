'''
Plot characteristic pr char maps for compressor
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import fhgcd_plots.main as fhgCD

df = pd.read_csv('compressor_results1.csv',sep=',')
df0 = pd.read_csv('charmap_simulation_results1.csv',sep=',')
df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
df1_10 = df1['Column6'][::10]

#df['X'].to_excel('X_values.xlsx', index=False, header=['Column1']) 

m1_design = 116.84458779580719
pr1_design = 5.096810782032807
p1_design = 1.9620112316612908 # in bar
e1_design = 0.8



fhgCD.set_matplotlib_style("darkgrid", "official")
fig, ax = plt.subplots(figsize=(10, 4))

x = df['Speed line X'].round(4)
y = (df['Comp1 m'].to_numpy() * p1_design) /(m1_design * df1['Column6'] * x * (1-df['igva1']/100))
z = df['pr1']/(pr1_design * (1 - df['igva1'] / 100))


new_df = pd.DataFrame({
    'x': x,
    'y': y,
    'z': z
})
fig1, ax = plt.subplots(figsize=(10, 4))
#x_values_to_plot = x.dropna().unique()
x_values_to_plot = [   0.9595,
   0.9666,
   0.9913,
   0.9914,
   0.9915,
   0.9916,
   0.9927,
   0.9928,
   0.9929,
   0.993
  ]


x_all = []
y_all = []
z_all = []
results = []

for x_value in x_values_to_plot:
    filtered_df = new_df[new_df['x'] == x_value]

    y_data = filtered_df['y'].to_numpy()
    z_data = filtered_df['z'].to_numpy()

    y_count = len(y_data)

    # Fit a 2nd-degree polynomial
    coeffs = np.polyfit(y_data, z_data, deg=2)
    poly = np.poly1d(coeffs)

    # Generate smooth points for the curve
    y_smooth = np.linspace(y_data.min(), y_data.max(), 10)
    z_smooth = poly(y_smooth)

  
    z_pred=poly(y_data)

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
    ax.plot(y_smooth, z_smooth,linestyle="-")
    plt.title('Pressure ratio curve fitting for Compressor stage 1')
    plt.xlabel('Y')
    plt.ylabel('Z')
    plt.legend(loc='lower right', bbox_to_anchor=(0.98, 0.02), fontsize=7)
    plt.grid(True)

print(f' "x" : {x_values_to_plot},\n "y" : {y_all},\n "z" :  {z_all}')
results_df = pd.DataFrame(results, columns=['X','R2','RMSE','MAPE','COUNT'])
results_df.to_csv('pr1_fit.csv', index=False)

plt.savefig("fit_pr1.png", dpi=300, bbox_inches="tight")
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

