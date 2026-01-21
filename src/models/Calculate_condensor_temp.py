'''
Calculate condensor temperature from given condensor pressure(Column9) from datasheet
'''
import pandas as pd
from tqdm import tqdm 
from CoolProp.CoolProp import PropsSI

df = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data

n_steps = len(df)
results = []
for step in tqdm(range(0,n_steps,1), desc="Calculation"):
    cond_temp = PropsSI('T','P',df['Column9'].iloc[step]*1e5,'Q',0,'R1234ZE') - 273.15 
    results.append(round(cond_temp,2))

results_df = pd.DataFrame(results)
results_df.to_csv('condensor temps.csv', index=False) # this is for full 13k data run
