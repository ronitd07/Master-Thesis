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
import json

df = pd.read_csv('compressor_results1.csv',sep=',')
df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data


def eta1_map():
    """
    Computes x, y, z arrays for a compressor map.
    If e_design is given, computes efficiency map; otherwise can be pressure ratio.
    """
    m1_design = 116.84458779580719
    pr1_design = 5.066214041567378
    p1_design = 1.9620112316612908 # in bar
    e1_design = 0.8


    #fhgCD.set_matplotlib_style("scientific", "official")
    #fig, ax = plt.subplots(figsize=(10, 4))

    x = df['Speed line X'].round(4)
    y = (df['Comp1 m'].to_numpy() * p1_design) /(m1_design * df1['Column6'] * x * (1-df['igva1']/100))
    z = df['Comp1 eff']/(e1_design * (1 - df['igva1']**2 / 10000))

    new_df = pd.DataFrame({
        'x': x,
        'y': y,
        'z': z
    })

    fig1, ax = plt.subplots(figsize=(10, 4))
    x_values_to_plot = np.sort(x.unique())
    #x_values_to_plot = [val for val in x_values_to_plot if 0.98 < val < 0.9999]
    x_values_to_plot = [

   0.9595,
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
        #print(f'{x_value} : count {len(y_data)}')
        #print(f'{x_value}, y_min {np.min(y_data)}, y_max {np.max(y_data)}')
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
        
    return x_values_to_plot,y_all,z_all

def pr1_map():

    m1_design = 116.84458779580719
    pr1_design = 5.066214041567378
    p1_design = 1.9620112316612908 # in bar
    e1_design = 0.8


    x = df['Speed line X'].round(4)
    y = (df['Comp1 m'].to_numpy() * p1_design) /(m1_design * df1['Column6'] * x * (1-df['igva1']/100))
    z = df['pr1']/(pr1_design * (1 - df['igva1'] / 100))

    new_df = pd.DataFrame({
        'x': x,
        'y': y,
        'z': z
    })
    #x_values_to_plot = x.dropna().unique()
    x_values_to_plot = [0.9646, 0.9705, 0.9713, 0.9714, 0.9715, 0.9718, 0.9724, 0.9889, 0.9912, 0.9913]

    y_all = []
    z_all = []

    for x_value in x_values_to_plot:
        filtered_df = new_df[new_df['x'] == x_value]

        y_data = filtered_df['y'].to_numpy()
        z_data = filtered_df['z'].to_numpy()

        # Fit a 2nd-degree polynomial
        coeffs = np.polyfit(y_data, z_data, deg=2)
        poly = np.poly1d(coeffs)

        # Generate smooth points for the curve
        y_smooth = np.linspace(y_data.min(), y_data.max(), 10)
        z_smooth = poly(y_smooth)

        # Store values
        y_all.append(y_smooth.tolist())
        z_all.append(z_smooth.tolist())
        

    return x_values_to_plot,y_all,z_all
def eta2_map():

    m2_design = 177.78266463515115
    pr2_design = 2.8615636254804433
    p2_design = 10 # in bar
    e2_design = 0.75


    x = df['Speed line x'].round(4)
    y = (df['Comp2 m'].to_numpy() * p2_design) /(m2_design * df1['Column19'] * x * (1-df['igva2']/100))
    z = df['Comp2 eff']/(e2_design * (1 - df['igva2']**2 / 10000))

    new_df = pd.DataFrame({
        'x': x,
        'y': y,
        'z': z
    })

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

    y_all = []
    z_all = []
    results = []

    for x_value in x_values_to_plot:
        filtered_df = new_df[new_df['x'] == x_value]

        y_data = filtered_df['y'].to_numpy()
        z_data = filtered_df['z'].to_numpy()
        #print(f'{x_value} : count {len(y_data)}')
        #print(f'{x_value}, y_min {np.min(y_data)}, y_max {np.max(y_data)}')
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


    return x_values_to_plot,y_all,z_all
def pr2_map():

    m2_design = 177.78266463515115
    pr2_design = 2.8615636254804433
    p2_design = 10 # in bar
    e2_design = 0.75

    x = df['Speed line x'].round(4)
    y = (df['Comp2 m'].to_numpy() * p2_design) /(m2_design * df1['Column19'] * x * (1-df['igva2']/100))
    z = df['pr2']/(pr2_design * (1 - df['igva2'] / 100))

    new_df = pd.DataFrame({
        'x': x,
        'y': y,
        'z': z
    })

    x_values_to_plot = [0.9966, 0.9978, 0.9979, 0.998, 0.9986, 0.9987, 0.9991, 0.9994, 0.9996, 0.9999]

    y_all = []
    z_all = []

    for x_value in x_values_to_plot:
        filtered_df = new_df[new_df['x'] == x_value]

        y_data = filtered_df['y'].to_numpy()
        z_data = filtered_df['z'].to_numpy()

        # Fit a 2nd-degree polynomial
        coeffs = np.polyfit(y_data, z_data, deg=2)
        poly = np.poly1d(coeffs)

        # Generate smooth points for the curve
        y_smooth = np.linspace(y_data.min(), y_data.max(), 10)
        z_smooth = poly(y_smooth)

        # Store values
        y_all.append(y_smooth.tolist())
        z_all.append(z_smooth.tolist())

    return x_values_to_plot,y_all,z_all



def create_compressor_map():
    x_eta1, y_eta1, z_eta1 = eta1_map()
    x_pr1, y_pr1, z_pr1 = pr1_map()
    x_eta2, y_eta2, z_eta2 = eta2_map()
    x_pr2, y_pr2, z_pr2 = pr2_map()

    # Add boundaries for eta1 map
    x_eta1_full = [0.946] + x_eta1 + [1]
    y_eta1_full = [[0.767, 0.805, 0.838, 0.859, 0.87,0.876, 0.878, 0.878, 0.879, 0.88]] + y_eta1 + [[0.3599170776552211, 0.4183788243324065, 0.4768405710095919, 0.5353023176867773, 0.5937640643639622, 0.6522258110411471, 0.7106875577183325, 0.7691493043955178, 0.8276110510727032, 0.8860727977498886]]
    z_eta1_full = [[0.891, 0.918, 0.946, 0.973, 1.001,1.014, 1.015, 0.986, 0.955, 0.925]] + z_eta1 + [[1.2182061632012324, 1.2634030454343312, 1.2930603002874346, 1.3071779277605384, 1.305755927853644, 1.2887943005667513, 1.256293045899863, 1.2082521638529764, 1.1446716544260904, 1.065551517619208]]

    # Add boundaries for pr1 map
    x_pr1_full = [0.946]  + x_pr1 + [1]
    y_pr1_full = [[0.767, 0.805, 0.838, 0.859, 0.87,0.876, 0.878, 0.878, 0.879, 0.88]] + y_pr1 + [[0.948, 0.974, 0.987, 0.995, 1.0,1.002, 1.005, 1.005, 1.006, 1.006]]
    z_pr1_full = [[0.931, 0.917, 0.893, 0.859, 0.82, 0.779, 0.738, 0.698, 0.657, 0.616]] + z_pr1 + [[1.195, 1.151, 1.102, 1.052, 1.0,0.951, 0.9, 0.85, 0.799, 0.748]]

    # Add boundaries for eta2 map
    x_eta2_full = [0.946] + x_eta2 + [1.029]
    y_eta2_full = [[0.767, 0.805, 0.838, 0.859, 0.87,0.876, 0.878, 0.878, 0.879, 0.88]] + y_eta2 + [[1.014, 1.017, 1.02, 1.023, 1.026,1.028, 1.03, 1.032, 1.034, 1.036]]
    z_eta2_full = [[0.891, 0.918, 0.946, 0.973, 1.001,1.014, 1.015, 0.986, 0.955, 0.925]] + z_eta2 + [[0.948, 0.959, 0.962, 0.949, 0.935,0.922, 0.908, 0.895, 0.881, 0.868]]

    # Add boundaries for pr2 map
    x_pr2_full = [0.946]  + x_pr2 + [1.029]
    y_pr2_full = [[0.767, 0.805, 0.838, 0.859, 0.87,0.876, 0.878, 0.878, 0.879, 0.88]] + y_pr2 + [[1.014, 1.017, 1.02, 1.023, 1.026,1.028, 1.03, 1.032, 1.034, 1.036]]
    z_pr2_full = [[0.931, 0.917, 0.893, 0.859, 0.82, 0.779, 0.738, 0.698, 0.657, 0.616]] + z_pr2 + [[1.34, 1.276, 1.213, 1.149, 1.085,1.022, 0.958, 0.894, 0.831, 0.767]]

    # Update map_data
    map_data = {
        "map_eta1": {"x": x_eta1_full, "y": y_eta1_full, "z": z_eta1_full},
        "map_pr1": {"x": x_pr1_full, "y": y_pr1_full, "z": z_pr1_full},
        "map_eta2": {"x": x_eta2_full, "y": y_eta2_full, "z": z_eta2_full},
        "map_pr2": {"x": x_pr2_full, "y": y_pr2_full, "z": z_pr2_full}
}
    
    with open(r"C:\Users\ron99091\.tespy\data\char_maps.json", "w") as f:
        json.dump(map_data,f,indent=1, cls=SmartEncoder)

class SmartEncoder(json.JSONEncoder):
    def iterencode(self, obj, _one_shot=False):
        for chunk in super().iterencode(obj, _one_shot=_one_shot):
            yield chunk

    def encode(self, obj):
        if isinstance(obj, list):
            # Keep small lists in one line
            if len(obj) <= 5 and all(isinstance(i, (int, float)) for i in obj):
                return '[' + ', '.join(map(str, obj)) + ']'
        return super().encode(obj)
    


if __name__ == "__main__":
    create_compressor_map()