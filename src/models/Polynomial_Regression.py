'''
Perform polynomial regression 
'''
import matplotlib.pyplot as plt
import pandas as pd
import fhgcd_plots.main as fhgCD
import matplotlib.dates as mdates
import numpy as np
from tqdm import tqdm 


df1 = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
df1_5 = df1.iloc[:5:1]
df2 = pd.read_csv('simulation_results.csv',sep=',')


P_tot_real = df1_5['Column22'] *1e3 # in W

eta_s1_corrected_list = []
eta_s2_corrected_list = []

for step in tqdm(range(0,5,1), desc="Calculation"):
 
    P_real1 = (P_tot_real.iloc[step] * df2['Compressor Power1 [W]'].iloc[step])/(df2['Compressor Power1 [W]'].iloc[step] + df2['Compressor Power2 [W]'].iloc[step])
    P_real2 = P_tot_real.iloc[step] - P_real1

    # Print the values
    print(f"Step {step+1}: P_real1 = {P_real1:.2f} W, P_real2 = {P_real2:.2f} W")

    eta_s1_corrected = df2['Compressor1 eff'].iloc[step] * df2['Compressor Power1 [W]'].iloc[step] / P_real1
    eta_s2_corrected = df2['Compressor2 eff'].iloc[step] * df2['Compressor Power2 [W]'].iloc[step] / P_real2

    eta_s1_corrected_list.append(eta_s1_corrected)
    eta_s2_corrected_list.append(eta_s2_corrected)

    print(f"Step {step+1}: eta1 = {eta_s1_corrected} , eta2 = {eta_s2_corrected} ")
results_df = pd.DataFrame()
results_df['eta_s1_corrected_df'] = eta_s1_corrected_list
results_df['eta_s2_corrected_df'] = eta_s2_corrected_list

results_df.to_csv('corrected_efficiency.csv', index=False)