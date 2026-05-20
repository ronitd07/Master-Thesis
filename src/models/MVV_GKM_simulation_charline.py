'''
This code simulates the heatpump cycle for Maneheim over an year using charline
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import CoolProp.CoolProp as CP
from heatpump_MVV_GKM_charline import Heatpump_tespy

from tqdm import tqdm 


def simulation_loop():
    # Define example parameters for heat pump

    params_hp = {
        "name": "MyHeatPump",
        "working_fluid": "R1234ZE",
        "cooling_mode #not implemented": False,
        "eta_compressor": 0.8,
        "eta_pump": 0.75,
        "ttd_heat_exchanger": 5.0,
        "heating_system_feed_temp": 100,
        "heating_system_return_temp": 60,    
        "tamb_design": 5.35,
        "heat_design": 22e6        # 22 MW as nominal load

    }

    #df = pd.read_excel('data/process_data/Manheim_data_cleaned3.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
    df = pd.read_excel('data/process_data/Manheim_data_cleaned.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
    #df = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="test", header=0,skiprows=range(1, 5)) #Load profile data


    thermal_loads = df['Column30'] * 1e6 # in Watts (Q at condenser)
    Q_nominal = max(df['Column30']) # Max q load or nominal load in Mw

    #date time data
    datetime = df['Column1']

    # source in/output temperature data
    source_in_temp = df['Column27']  # in °C
    source_out_temp = df['Column28']  # in °C

    # sink in/output temperature data
    sink_in_temp = df['Column24'] # in °C
    sink_out_temp = df['Column23'] # in °C

    #Intermediate pressure at flash tank
    inter_p = df['Column19'] # in bar

    #evap and condensor temp data
    evap_temp = df['Column7'] # in °C Not used
    cond_temp = df['Column11'] # in °C temperature at compressor2 out

    #Condensor pressure
    cond_p = df['Column9'] # in bar

    #Temperature behind the subcooler
    subcooler_t = df['Column16'] # in °C

    # Compressor1 inlet superheat
    comp1_sp = df['Column8'].abs() # in °C

    #Compressor real powers


    heatpump_model = Heatpump_tespy(params_hp)

    print("Heatpump design mode successful")

    n_steps = len(df)
    results=[]
    heatpump_model.x1 = []
    heatpump_model.x2 = []

    count = 0

    for step in tqdm(range(0,n_steps,1), desc="Calculation"):
        current_time = datetime.iloc[step]
        sink_temp_in = sink_in_temp.iloc[step]
        sink_temp_out = sink_out_temp.iloc[step]
        source_temp_in = source_in_temp.iloc[step]
        source_temp_out = source_out_temp.iloc[step]
        Q_load = thermal_loads.iloc[step]
        p_inter = inter_p.iloc[step]
        t_evap = evap_temp.iloc[step]
        t_cond = cond_temp.iloc[step]
        sp_comp1 = comp1_sp.iloc[step]
        p_cond = cond_p.iloc[step]
        t_subcooler = subcooler_t.iloc[step]
        count +=1
        try:
            # Step heat pump simulation
            t_in_cp1,t_in_cp2, p_in_cp1, p_in_cp2, eta1, eta2, m1, m2, pr1, pr2,cop,ratio,cp1,cp2 = heatpump_model.calc_partload_state(sink_temp_in,sink_temp_out, source_temp_in,source_temp_out,Q_load,p_inter,t_evap,t_cond,sp_comp1,p_cond,t_subcooler)

            results.append({
                'datetime': current_time,
                'Temp in cp1' : t_in_cp1,
                'Temp in cp2' : t_in_cp2,
                'Pressure in cp1' : p_in_cp1,
                'Pressure in cp2' : p_in_cp2,
                'Comp1 eff' : eta1,
                'Comp2 eff' : eta2,
                'Comp1 m' : m1,
                'Comp2 m' : m2,
                'pr comp1' : pr1,
                'pr comp2' : pr2,
                'cop' : cop,
                'cop_given' : df['Column4'].iloc[step],
                'ratio' : ratio,
                'cp1' : cp1,
                'cp2' : cp2,
                'status': 'passed'
            })
            
        except Exception as e:
            print(f"❌ Failed at step {step}, time {current_time}: {e}")

            results.append({
                'datetime': current_time,
                'Temp in cp1' : None,
                'Temp in cp2' : None,
                'Pressure in cp1' : None,
                'Pressure in cp2' : None,
                'Comp1 eff' : None,
                'Comp2 eff' : None,
                'Comp1 m' : None,
                'Comp2 m' : None,
                'pr comp1' : None,
                'pr comp2' : None,
                'cop' : cop,
                'cop_given' : df['Column4'].iloc[step],
                'ratio' : None,
                'cp1' : None,
                'cp2' : None,
                'status': 'failed',
                'error': str(e)
            })

            continue
    results_df = pd.DataFrame(results)
    results_df.to_csv('charline_simulation_results.csv', index=False) 

    n_failed = (results_df['status'] == 'failed').sum()
    print(f'Failed count : {n_failed} out of {count}')


if __name__ == "__main__":
    simulation_loop()