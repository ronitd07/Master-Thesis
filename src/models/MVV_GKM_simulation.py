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
    df = pd.read_excel('data/process_data/Manheim_data.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 76)) #Load profile data
    #df['date_time_clean'] = df['Zeit'].str.split(', ').str[1]
    #df['datetime'] = pd.to_datetime('2023 ' + df['date_time_clean'], format='%Y %d.%m. %H:%M')
    #df['datetime'] = df['datetime'].dt.strftime('%d%m%Y')
    #df = df.sort_values('datetime')

    #Cooling load
    #df_cooling_load = pd.read_excel('data/inputs/load_profiles/241213_Wärme_Kälte_Bedarfe_und_Lastgänge.xlsx', index_col=0, sheet_name='Lastgänge_Kälte_in_kW')
    #df_cooling_load_sum = df_cooling_load.sum(axis=1)*1000

    # Thermal loads data 
    #df['Column30'] = pd.to_numeric(df['Column30'], errors='coerce')
    thermal_loads = df['Column30'] * 1e6 # in Watts (Q at condenser)

    #date time data
    datetime = df['Column1']

    # source temperature data
    source_input_temp = df['Column27']  # in °C

    heatpump_model = Heatpump_tespy(params_hp)

    print("Heatpump design mode successful")

    n_steps = len(df)
    results=[]


    for step in tqdm(range(n_steps), desc="Calculation"):
        current_time = datetime.iloc[step]
        Q_load = thermal_loads.iloc[step]
        source_temp = source_input_temp.iloc[step]
        if Q_load <= 0:
            results.append({
            'datetime': current_time,
            'Souce_temp':  source_temp,
            'Q_load [W]': Q_load,
            'COP': None,
            'Compressor Power [W]': None
        })
            continue
        try:
            # Step heat pump simulation
            cop, power = heatpump_model.step(Q_load, source_temp)

            results.append({
                'datetime': current_time,
                'Souce_temp':  source_temp,
                'Q_load [W]': Q_load,
                'COP': cop,
                'Compressor Power [W]': power,
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
'''
results=[]

    for step in tqdm(range(n_steps), desc="Calculation"):
        #current_time = step * step_size / 3600  # hours
        current_time = df["datetime"].iloc[step]

        # Step BHE simulation
        bhe_model.step()

        # Extract BHE outputs for heat pump input
        df["load_W"] = df["load_kW"] * 1000  # convert load from kW to W
        Q_load = df["load_W"].iloc[step]

        ambient_temp = bhe_model.T_out  # Outlet temperature from BHE
        if Q_load == 0:
            results.append({
            'datetime': current_time,
            'T_out_BHE [°C]':  ambient_temp,
            'Q_load [W]': Q_load,
            'COP': None,
            'Compressor Power [W]': None
        })
            continue
        try:
            # Step heat pump simulation
            cop, power, load, T_delta,m_flow = heatpump_model.step(Q_load, ambient_temp)
            T_out = heatpump_model.evap_outlet_temperature()

            results.append({
                'datetime': current_time,
                'T_out_BHE [°C]':  ambient_temp,
                'Q_load [W]': Q_load,
                'COP': cop,
                'Compressor Power [W]': power,
                'Condensor load[W]' : load,
                'Temp lift[°C]' : T_delta,
                'error': None
            })
            if df_cooling_load_sum.iloc[step] > 0:
                Q_cooling = df_cooling_load_sum.iloc[step]
                T_in = hx_cooling.c20.T.val
                hx_cooling.step(current_time, -Q_cooling, T_in)
                temp1 = hx_cooling.c21.T.val
                dotm_1 = hx_cooling.c21.m.val
                
                T_out = (T_out*m_flow+dotm_1*temp1)/(m_flow+dotm_1)
                dotm_out = dotm_1+m_flow
                bhe_model.dotm_in = dotm_out
                bhe_model.T_in = T_out
            else:
                bhe_model.dotm_in = m_flow
                bhe_model.T_in = T_out
        except Exception as e:
            print(f"\n❌ Error at step {step}, time {current_time}")
            print(f"   Q_load = {Q_load}, ambient_temp = {ambient_temp}")
            raise e 

    results_df = pd.DataFrame(results)
    results_df.to_csv('combined_simulation_results.csv', index=False)
    average_COP = results_df['COP'].mean()
    print("Average COP:", average_COP)

    #Convert from W to kW
    compressor_power_kW = results_df["Compressor Power [W]"] / 1000
    condensor_load_kW = results_df["Condensor load[W]"]/1000
    cop_cal = condensor_load_kW/compressor_power_kW

    #COP over the year
    plt.figure(figsize=(10,5))
    plt.plot( results_df["datetime"],results_df["COP"], marker='o', color='purple')
    #plt.plot( results_df["datetime"],cop_cal, marker='x', color='yellow')
    plt.title('COP vs Time')
    plt.xlabel('Date')
    plt.ylabel('COP')
    plt.grid(True)
    plt.tight_layout()

    #Temperature lift over the year
    plt.figure(figsize=(10,5))
    plt.plot( results_df["datetime"],results_df["Temp lift[°C]"], marker='o', color='purple')
    plt.title('Temperature lift vs Time')
    plt.xlabel('Date')
    plt.ylabel('Temperature lift [°C]')
    plt.grid(True)
    plt.tight_layout()
    
    #Load and Power over the year
    plt.figure(figsize=(10,5))
    plt.plot( results_df["datetime"],compressor_power_kW, marker='o', color='red',label='Compressor Power [kW]')
    plt.plot( results_df["datetime"],condensor_load_kW, marker='o', color='black',label='Condensor Load [kW]' )
    plt.title('Compressor Power and Condensor Load vs Time')
    plt.xlabel('Date')
    plt.ylabel('Power/Load [kW]')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()  
    
    plt.show()
    '''

if __name__ == "__main__":
    simulation_loop()