'''
This code simulates the heatpump cycle for Maneheim over an year
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import CoolProp.CoolProp as CP
#from heatpump_MVV_GKM import Heatpump_tespy
#from heatpump_MVV_GKM_subcooling import Heatpump_tespy
from heatpump_MVV_GKM_compressorP import Heatpump_tespy
#from models.mosaik_models.restructure_heatpump_tespy import HeatPump
from tqdm import tqdm 


def simulation_loop():
    # Define example parameters for heat pump

    params_hp = {
        "name": "MyHeatPump",
        "working_fluid": "R1234ZE",
        "cooling_mode #not implemented": False,
        "eta_compressor": 0.85,
        "eta_pump": 0.7,
        "ttd_heat_exchanger": 5.0,
        "heating_system_feed_temp": 101.32,
        "heating_system_return_temp": 57.01,
        "cooling_system_feed_temp": 10.0,
        "cooling_system_return_temp": 15.0,        
        "tamb_design": 5.35,
        "heat_design": 22e6,        # 22 MW as nominal load
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
    #df = pd.read_excel('data/process_data/Manheim_data_cleaned3.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
    df = pd.read_excel('data/process_data/Manheim_data_cleaned4.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0,skiprows=range(1, 5)) #Load profile data
    #df = pd.read_excel('data/process_data/Manheim_data_cleaned3.xlsx', sheet_name="test", header=0,skiprows=range(1, 5)) #Load profile data
    df2 = pd.read_csv('corrected_efficiency.csv',sep=',')


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
        cp1_real = df['Column37'].iloc[step] # in kW
        cp2_real = df['Column38'].iloc[step] # in kW

        try:
            # Step heat pump simulation
            eta1,eta2,m1,m2,pr1,pr2,X,x,cop= heatpump_model.calc_partload_state(sink_temp_in,sink_temp_out, source_temp_in,source_temp_out,Q_load,p_inter,t_evap,t_cond,sp_comp1,p_cond,t_subcooler,cp1_real,cp2_real)

            results.append({
                'datetime': current_time,
                'Comp1 eff' : eta1,
                'Comp2 eff' : eta2,
                'Comp1 m' : m1,
                'Comp2 m' : m2,
                'pr1' : pr1,
                'pr2' : pr2,
                'X' : X,
                'x' : x,
                'cop' : cop,
                'cop_given' : df['Column4'].iloc[step],
                'error': None 
            })
        except Exception as e:
            print(f"\n❌ Error at step {step}, time {current_time}")
            print(f"   Sink_temp = {sink_temp_out}, ambient_temp = {source_temp_in}")
            raise e
    results_df = pd.DataFrame(results)
    results_df.to_csv('compressor_results.csv', index=False)
    #results_df.to_csv('simulation_results.csv', index=False)


    print("Nominal load (MW):", Q_nominal)

    '''
    x1_df = pd.DataFrame(heatpump_model.x1)
    print(x1_df)
    x2_df = pd.DataFrame(heatpump_model.x2)
    print(x2_df)

    # Given compressor powers in kW
    y1_df=df['Column37'][:5]
    y2_df=df['Column38'][:5]





  

    from sklearn.linear_model import LinearRegression
    model1 = LinearRegression()
    model1.fit(x1_df,y1_df)
    p1 = model1.predict(x1_df)
    print(p1)

    model2 = LinearRegression()
    model2.fit(x2_df,y2_df)
    p2 = model2.predict(x2_df)
    print(p2)

    df_pred = pd.DataFrame({
        "Prediction1": p1,   # predictions from model1
        "Prediction2": p2    # predictions from model2
    })

    df_pred.to_csv("power_predictions.csv", index=False)

    '''
    #Plot the eta_s curve, PH, TS plots, TQ plot
    #heatpump_model.plot_eta_s()
    #heatpump_model.generate_state_diagram(diagram_type='Ts', savefig=True, open_file=False)
    #heatpump_model.generate_state_diagram(diagram_type='logph', savefig=True, open_file=False)

    # To generate temperature profile at condensor and evaporator using custom method 
    #heatpump_model.generate_temp_plot()

    # To generate temperature profile at condensor using TESPY method 
    #heatpump_model.generate_temp_plot2()
 
    # Adjust layout
    plt.tight_layout()
    #plt.show()


if __name__ == "__main__":
    simulation_loop()