'''
This code simulates the heatpump cycle for Maneheim over an year
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import CoolProp.CoolProp as CP
from heatpump_MVV_GKM import Heatpump_tespy
#from models.mosaik_models.restructure_heatpump_tespy import HeatPump
from tqdm import tqdm 


def simulation_loop():
    # Define example parameters for heat pump

    params_hp = {
        "name": "MyHeatPump",
        "working_fluid": "R1234ZE",
        "cooling_mode #not implemented": False,
        "eta_compressor": 0.8,
        "eta_fan": 0.7,
        "ttd_heat_exchanger": 5.0,
        "heating_system_feed_temp": 80.0,
        "heating_system_return_temp": 30.0,
        "cooling_system_feed_temp": 10.0,
        "cooling_system_return_temp": 15.0,        
        "tamb_design": 8,
        "heat_design": 100e3,        # 100 kW
        "cooling_Q_design": 50e3,    # 50 kW
        "cooling_tamb_design": 25.0
    }
    params_cooling = {
        "name": "hx_cooling",
        "eta_pump": 0.85,
        "primary_side_fluid": "Water",
        "secondary_side_fluid": "INCOMP::MPG[0.2]|mass",
        "primary_side_feed_temp": 25,
        "primary_side_return_temp": 15,
        "pr1_heat_exchanger": 0.99,
        "pr2_heat_exchanger": 0.99,
        "ttd_u_heat_exchanger": 2,
        "design":
        {
            "Q_load": -323e3,
            "dotm_pri": 7.6
        }
    }
    df = pd.read_excel('data/process_data/Manheim_data_cleaned2.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
    #df = pd.read_excel('data/process_data/Manheim_data_cleaned2.xlsx', sheet_name="test", header=0,skiprows=range(1, 5)) #Load profile data

    thermal_loads = df['Column30'] * 1e6 # in Watts (Q at condenser)

    #date time data
    datetime = df['Column1']

    # source input and output temperature data
    source_input_temp = df['Column27']  # in °C
    source_output_temp = df['Column28'] # in °C

    heatpump_model = Heatpump_tespy(params_hp)

    print("Heatpump design mode successful")

    n_steps = len(df)
    results=[]


    for step in tqdm(range(n_steps), desc="Calculation"):
        current_time = datetime.iloc[step]
        Q_load = thermal_loads.iloc[step]
        source_temp = source_input_temp.iloc[step]
        '''
        if Q_load <= 0:
            results.append({
            'datetime': current_time,
            'Souce_temp':  source_temp,
            'Q_load [W]': Q_load,
            'COP': None,
            'Compressor Power [W]': None
        })
            continue
            '''
        try:
            # Step heat pump simulation
            cop, power,load = heatpump_model.step(Q_load, source_temp)

            results.append({
                'datetime': current_time,
                'Souce_temp':  source_temp,
                'Q_load [W]': Q_load,
                'COP': cop,
                'Compressor Power [W]': power,
                'Condensor load[W]' : load,
                'error': None
            })
        except Exception as e:
            print(f"\n❌ Error at step {step}, time {current_time}")
            print(f"   Q_load = {Q_load}, ambient_temp = {source_temp}")
            raise e
    results_df = pd.DataFrame(results)
    results_df.to_csv('combined_simulation_results.csv', index=False)
    average_COP = results_df['COP'].mean()
    print("Average COP:", average_COP) 

    #COP over the year
    plt.plot( results_df["datetime"],results_df["COP"], marker='o', color='purple')
    plt.title('COP vs Time')
    plt.xlabel('Date')
    plt.ylabel('COP')
    plt.grid(True)

    # Adjust layout
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    simulation_loop()