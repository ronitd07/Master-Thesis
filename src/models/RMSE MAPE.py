'''
compute RMSE and MAPE of the COP obtained
'''
import pandas as pd
import numpy as np

df = pd.read_csv('charmap_simulation_results_0.864.csv',sep=',')
#df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
#df2 = pd.read_csv('charmap_simulation_results9.csv',sep=',')

#df9 = pd.read_csv('charmap_simulation_results9.csv',sep=',')
#df8 = pd.read_csv('charmap_simulation_results8.csv',sep=',')
#df = pd.concat([df8, df9])


def rmse(y_measured, y_model):
    y_measured = np.array(y_measured)
    y_model = np.array(y_model)
    return np.sqrt(np.mean((y_model - y_measured)**2))


def mape(y_measured, y_model):
    y_measured = np.array(y_measured)
    y_model = np.array(y_model)
    return np.mean(np.abs((y_model - y_measured) / y_measured)) * 100


y_measured = df['cop_given'].dropna()
y_model    = df['cop'].dropna()

# Remove outliers with cop < 2.6
#df2_filtered = df2[df2['cop_given'] > 2.4]
#y_measured  = df2_filtered['cop_given']
#y_model  = df2_filtered['cop']

rmse_value = rmse(y_measured, y_model)
mape_value = mape(y_measured, y_model)

print(f"RMSE = {rmse_value:.3f} ")
print(f"MAPE = {mape_value:.2f} %")
